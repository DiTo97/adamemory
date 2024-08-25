"""
telemetry module
"""
import platform
import sys
import importlib
from posthog import Posthog

class AnonymousTelemetry:
    """
    Singleton class for capturing anonymous telemetry data using Posthog.
    """
    _instance = None

    @classmethod
    def get_instance(cls, **kwargs):
        """
        Returns the singleton instance of AnonymousTelemetry.

        :param kwargs: Additional keyword arguments for initializing the instance
        :return: The singleton instance of AnonymousTelemetry
        :rtype: AnonymousTelemetry
        """
        if cls._instance is None:
            cls._instance = cls(**kwargs)
        return cls._instance

    def __init__(self, project_api_key, host):
        """
        Initializes the AnonymousTelemetry instance.

        :param project_api_key: The API key for the Posthog project
        :type project_api_key: str
        :param host: The host URL for the Posthog instance
        :type host: str
        """
        self.posthog = Posthog(project_api_key=project_api_key, host=host)

    def capture_event(self, event_name, properties=None):
        """
        Captures an event with the given properties.

        :param event_name: The name of the event to capture
        :type event_name: str
        :param properties: Additional properties for the event, defaults to None
        :type properties: dict, optional
        """
        if properties is None:
            properties = {}
        properties.update({
            "python-version": sys.version,
            "OS": sys.platform,
            "OS-version": platform.version(),
            "OS-release": platform.release(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "version": ".".join([str(i) for i in importlib.metadata.version("adamemory").split(".")])
        })
        self.posthog.capture(
            distinct_id="<TODO>", event=event_name, properties=properties
        )

    def close(self):
        """
        Shuts down the Posthog client.
        """
        self.posthog.shutdown()

# Initialize AnonymousTelemetry
telemetry = AnonymousTelemetry.get_instance(
    project_api_key="<TODO>",
    host="https://eu.i.posthog.com"
)

def capture_event(event_name, memory_instance, additional_data=None):
    """
    Captures an event related to a memory instance.

    :param event_name: The name of the event to capture
    :type event_name: str
    :param memory_instance: The memory instance related to the event
    :type memory_instance: object
    :param additional_data: Additional data to include in the event, defaults to None
    :type additional_data: dict, optional
    """
    event_data = {
        "collection": memory_instance.collection_name,
        "embedding-dim": memory_instance.embedding_model.config.embedding_dims,
        "history-store": "sqlite",
        "language-model": f"{memory_instance.llm.__class__.__module__}.{memory_instance.llm.__class__.__name__}",
        "embedding": f"{memory_instance.embedding_model.__class__.__module__}.{memory_instance.embedding_model.__class__.__name__}",
        "function": f"{memory_instance.__class__.__module__}.{memory_instance.__class__.__name__}.{memory_instance.version}",
    }
    if additional_data:
        event_data.update(additional_data)

    telemetry.capture_event(event_name, event_data)

def capture_client_event(event_name, instance, additional_data=None):
    """
    Captures an event related to a client instance.

    :param event_name: The name of the event to capture
    :type event_name: str
    :param instance: The client instance related to the event
    :type instance: object
    :param additional_data: Additional data to include in the event, defaults to None
    :type additional_data: dict, optional
    """
    event_data = {
        "function": f"{instance.__class__.__module__}.{instance.__class__.__name__}",
    }
    if additional_data:
        event_data.update(additional_data)

    telemetry.capture_event(event_name, event_data)
