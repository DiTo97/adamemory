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
import logging
import uuid
from typing import Callable, Dict
from urllib import request

# Constants and Configurations
VERSION = importlib.metadata.version("adamemory")
STR_VERSION = ".".join([str(i) for i in VERSION])
HOST = "https://eu.i.posthog.com"
TRACK_URL = f"{HOST}/capture/"
API_KEY = "<TODO>"
TIMEOUT = 2
DEFAULT_CONFIG_LOCATION = os.path.expanduser("~/.adamemory.conf")
MAX_COUNT_SESSION = 1000

logger = logging.getLogger(__name__)

# Load Configuration
def _load_config(config_location: str) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    try:
        with open(config_location) as f:
            config.read_file(f)
    except Exception:
        config["DEFAULT"] = {}
    else:
        if "DEFAULT" not in config:
            config["DEFAULT"] = {}

    if "anonymous_id" not in config["DEFAULT"]:
        config["DEFAULT"]["anonymous_id"] = str(uuid.uuid4())
        try:
            with open(config_location, "w") as f:
                config.write(f)
        except Exception:
            pass
    return config

def _check_config_and_environ_for_telemetry_flag(
    telemetry_default: bool, config_obj: configparser.ConfigParser
) -> bool:
    telemetry_enabled = telemetry_default
    if "telemetry_enabled" in config_obj["DEFAULT"]:
        try:
            telemetry_enabled = config_obj.getboolean("DEFAULT", "telemetry_enabled")
        except ValueError as e:
            logger.debug(f"Unable to parse value for `telemetry_enabled` from config. Encountered {e}")
    if os.environ.get("ADAMEMORY_TELEMETRY_ENABLED") is not None:
        env_value = os.environ.get("ADAMEMORY_TELEMETRY_ENABLED")
        config_obj["DEFAULT"]["telemetry_enabled"] = env_value
        try:
            telemetry_enabled = config_obj.getboolean("DEFAULT", "telemetry_enabled")
        except ValueError as e:
            logger.debug(f"Unable to parse value for `ADAMEMORY_TELEMETRY_ENABLED` from environment. Encountered {e}")
    return telemetry_enabled

config = _load_config(DEFAULT_CONFIG_LOCATION)
g_telemetry_enabled = _check_config_and_environ_for_telemetry_flag(True, config)
g_anonymous_id = config["DEFAULT"]["anonymous_id"]
CALL_COUNTER = 0

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
    Function for disabling telemetry
    """
    global g_telemetry_enabled
    g_telemetry_enabled = False

def is_telemetry_enabled() -> bool:
    """
    Function for checking if telemetry is enabled
    """
    if g_telemetry_enabled:
        global CALL_COUNTER
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
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}",
        "User-Agent": f"adamemory/{STR_VERSION}",
    }
    try:
        data = json.dumps(event_json).encode()
        req = request.Request(TRACK_URL, data=data, headers=headers)
        with request.urlopen(req, timeout=TIMEOUT) as f:
            res = f.read()
            if f.code != 200:
                raise RuntimeError(res)
    except Exception as e:
        logger.debug(f"Failed to send telemetry data: {e}")
    else:
        logger.debug(f"Telemetry data sent: {data}")

def send_event_json(event_json: dict):
    """
    Function for sending event JSON
    """
    if not g_telemetry_enabled:
        raise RuntimeError("Telemetry tracking is disabled!")
    try:
        th = threading.Thread(target=_send_event_json, args=(event_json,))
        th.start()
    except Exception as e:
        logger.debug(f"Failed to send telemetry data in a thread: {e}")

def capture_event(event: str, properties: Dict[str, any]):
    """
    Function for logging events
    """
    if is_telemetry_enabled():
        event_json = {
            "api_key": API_KEY,
            "event": event,
            "properties": {**BASE_PROPERTIES, **properties},
        }
        send_event_json(event_json)

def capture_memory_event(memory_instance, additional_data=None):
    """
    Function for logging memory usage events
    """
    properties = {
        "collection": memory_instance.collection_name,
        "embedding_dim": memory_instance.embedding_model.config.embedding_dims,
        "history_store": "sqlite",
        "language_model": f"{memory_instance.llm.__class__.__module__}.{memory_instance.llm.__class__.__name__}",
        "embedding": f"{memory_instance.embedding_model.__class__.__module__}.{memory_instance.embedding_model.__class__.__name__}",
        "function": f"{memory_instance.__class__.__module__}.{memory_instance.__class__.__name__}.{memory_instance.version}",
    }
    if additional_data:
        properties.update(additional_data)

    capture_event("memory_event", properties)

def capture_function_usage(call_fn: Callable) -> Callable:
    """
    Decorator to capture telemetry for function usage
    """
    @functools.wraps(call_fn)
    def wrapped_fn(*args, **kwargs):
        try:
            return call_fn(*args, **kwargs)
        finally:
            if is_telemetry_enabled():
                try:
                    function_name = call_fn.__name__
                    capture_event("function_usage", {"function_name": function_name})
                except Exception as e:
                    logger.debug(f"Failed to send telemetry for function usage. Encountered: {e}")
    return wrapped_fn
