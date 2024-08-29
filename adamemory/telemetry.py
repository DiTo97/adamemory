"""
This module contains code that relates to sending Adamemory usage telemetry.
To disable sending telemetry, there are three ways:
1. Set it to false programmatically in your script:
  >>> from adamemory import telemetry
  >>> telemetry.disable_telemetry()
2. Set it to `false` in ~/.adamemory.conf under `DEFAULT`
  [DEFAULT]
  telemetry_enabled = False
3. Set ADAMEMORY_TELEMETRY_ENABLED=false as an environment variable:
  ADAMEMORY_TELEMETRY_ENABLED=false python run.py
  or:
  export ADAMEMORY_TELEMETRY_ENABLED=false
"""

import configparser
import functools
import importlib.metadata
import json
import os
import platform
import threading
import uuid
from functools import wraps
from typing import Callable, Dict
from urllib import request

from .common import only_once
from .logging import get_logger


# Importing the centralized logging system from the logging module
logger = get_logger(__name__)

# Constants and Configurations
VERSION = importlib.metadata.version("adamemory")
STR_VERSION = ".".join([str(i) for i in VERSION])
HOST = "https://eu.i.posthog.com"
TRACK_URL = f"{HOST}/capture/"
API_KEY = "<TODO>"
TIMEOUT = 2  # Timeout duration for HTTP requests in seconds
DEFAULT_CONFIG_LOCATION = os.path.expanduser("~/.adamemory.conf")
MAX_COUNT_SESSION = 1000  # Maximum number of telemetry events per session


# Load Configuration
@only_once
def _load_config(config_location: str) -> configparser.ConfigParser:
    """
    Load the configuration file from the specified location.
    If the file doesn't exist or cannot be read, a default configuration is created.

    Args:
        config_location (str): The path to the configuration file.

    Returns:
        configparser.ConfigParser: The loaded configuration object.
    """
    config = configparser.ConfigParser()
    try:
        with open(config_location) as f:
            config.read_file(f)
    except Exception:
        config["DEFAULT"] = {}  # Create an empty default configuration if reading fails
    else:
        if "DEFAULT" not in config:
            config["DEFAULT"] = {}  # Ensure the DEFAULT section exists

    # Generate and store an anonymous ID if it doesn't exist
    if "anonymous_id" not in config["DEFAULT"]:
        config["DEFAULT"]["anonymous_id"] = str(uuid.uuid4())
        try:
            with open(config_location, "w") as f:
                config.write(f)
        except Exception:
            pass  # Ignore write errors

    return config


@only_once
def _check_config_and_environ_for_telemetry_flag(
    telemetry_default: bool, config_obj: configparser.ConfigParser
) -> bool:
    """
    Check both the configuration file and environment variables for telemetry settings.
    This function determines if telemetry should be enabled or disabled.

    Args:
        telemetry_default (bool): The default telemetry setting if no configuration is found.
        config_obj (configparser.ConfigParser): The configuration object.

    Returns:
        bool: Whether telemetry is enabled or not.
    """
    telemetry_enabled = telemetry_default
    if "telemetry_enabled" in config_obj["DEFAULT"]:
        try:
            telemetry_enabled = config_obj.getboolean("DEFAULT", "telemetry_enabled")
        except ValueError as e:
            logger.debug(
                f"Unable to parse value for `telemetry_enabled` from config. Encountered {e}"
            )

    # Check for environment variable override
    if os.environ.get("ADAMEMORY_TELEMETRY_ENABLED") is not None:
        env_value = os.environ.get("ADAMEMORY_TELEMETRY_ENABLED")
        config_obj["DEFAULT"]["telemetry_enabled"] = env_value
        try:
            telemetry_enabled = config_obj.getboolean("DEFAULT", "telemetry_enabled")
        except ValueError as e:
            logger.debug(
                f"Unable to parse value for `ADAMEMORY_TELEMETRY_ENABLED` from environment. Encountered {e}"
            )

    return telemetry_enabled


# Load configuration and determine telemetry state at module import time
config = _load_config(DEFAULT_CONFIG_LOCATION)
g_telemetry_enabled = _check_config_and_environ_for_telemetry_flag(True, config)
g_anonymous_id = config["DEFAULT"][
    "anonymous_id"
]  # Retrieve the anonymous ID from config
CALL_COUNTER = 0  # Initialize the call counter for telemetry events

# Base properties for events
BASE_PROPERTIES = {
    "os_type": os.name,
    "os_version": platform.version(),
    "os_release": platform.release(),
    "processor": platform.processor(),
    "machine": platform.machine(),
    "python_version": f"{platform.python_version()}/{platform.python_implementation()}",
    "distinct_id": g_anonymous_id,
    "adamemory_version": VERSION,
    "telemetry_version": "0.0.1",
}


def disable_telemetry():
    """
    Function for disabling telemetry collection.
    This can be called programmatically to stop telemetry data from being sent.
    """
    global g_telemetry_enabled
    g_telemetry_enabled = False


def is_telemetry_enabled() -> bool:
    """
    Function for checking if telemetry is enabled.
    This function also increments the call counter and limits the number of events per session.

    Returns:
        bool: True if telemetry is enabled and the call counter is within limits, False otherwise.
    """
    global CALL_COUNTER
    if g_telemetry_enabled:
        if CALL_COUNTER == 0:
            logger.debug(
                "Note: Adamemory collects anonymous usage data to improve the library. "
                "You can disable telemetry by setting ADAMEMORY_TELEMETRY_ENABLED=false or "
                "by editing ~/.adamemory.conf."
            )
        CALL_COUNTER += 1
        if CALL_COUNTER > MAX_COUNT_SESSION:
            return False
        return True
    else:
        return False


# Sending and Logging Event Functions
def _send_event_json(event_json: dict):
    """
    Helper function to send telemetry data as JSON to the PostHog API.

    Args:
        event_json (dict): The event data to be sent.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": f"adamemory/{STR_VERSION}",
    }
    try:
        data = json.dumps(event_json).encode()  # Encode the event data to JSON format
        req = request.Request(
            TRACK_URL, data=data, headers=headers
        )  # Create the HTTP request
        with request.urlopen(req, timeout=TIMEOUT) as f:
            res = f.read()
            if f.code != 200:
                raise RuntimeError(res)
    except Exception as e:
        logger.debug(f"Failed to send telemetry data: {e}")  # Log any errors
    else:
        logger.debug(f"Telemetry data sent: {data}")


def send_event_json(event_json: dict):
    """
    Function to send telemetry event data asynchronously.
    This function spawns a new thread to send the event data.

    Args:
        event_json (dict): The event data to be sent.
    """
    if not g_telemetry_enabled:
        raise RuntimeError(
            "Telemetry tracking is disabled!"
        )  # Raise an error if telemetry is disabled
    try:
        th = threading.Thread(target=_send_event_json, args=(event_json,))
        th.start()  # Start a new thread to send the telemetry data
    except Exception as e:
        logger.debug(f"Failed to send telemetry data in a thread: {e}")


def capture_event(event: str, properties: Dict[str, any]):
    """
    Function to capture and send a telemetry event.

    Args:
        event (str): The name of the event.
        properties (Dict[str, any]): Additional properties related to the event.
    """
    if is_telemetry_enabled():
        event_json = {
            "api_key": API_KEY,
            "event": event,
            "properties": {**BASE_PROPERTIES, **properties},
        }
        send_event_json(event_json)  # Send the event data as JSON


def capture_memory_event(memory_instance, additional_data=None):
    """
    Function to log memory usage events for Adamemory.
    This function collects data related to memory usage and sends it as a telemetry event.

    Args:
        memory_instance: The memory instance object containing usage data.
        additional_data (dict, optional): Any additional data to include in the event.
    """
    # Collect relevant properties for the memory event
    properties = {
        "collection": memory_instance.collection_name,
        "embedding_dim": memory_instance.embedding_model.config.embedding_dims,
        "history_store": "sqlite",
        "language_model": f"{memory_instance.llm.__class__.__module__}.{memory_instance.llm.__class__.__name__}",
        "embedding": f"{memory_instance.embedding_model.__class__.__module__}.{memory_instance.embedding_model.__class__.__name__}",
        "function": f"{memory_instance.__class__.__module__}.{memory_instance.__class__.__name__}.{memory_instance.version}",
    }
    if additional_data:
        properties.update(additional_data)  # Add any additional data to the properties

    capture_event("memory_event", properties)  # Capture the memory usage event


def capture_function_usage(call_fn: Callable) -> Callable:
    """
    Decorator to capture telemetry for function usage.
    This decorator logs the function name whenever the wrapped function is called.

    Args:
        call_fn (Callable): The function to be wrapped and monitored.

    Returns:
        Callable: The wrapped function with telemetry capturing.
    """

    @functools.wraps(call_fn)
    def wrapped_fn(*args, **kwargs):
        try:
            return call_fn(*args, **kwargs)  # Call the original function
        finally:
            if is_telemetry_enabled():
                try:
                    function_name = call_fn.__name__  # Capture the function name
                    capture_event(
                        "function_usage", {"function_name": function_name}
                    )  # Log the function usage
                except Exception as e:
                    logger.debug(
                        f"Failed to send telemetry for function usage. Encountered: {e}"
                    )

    return wrapped_fn
