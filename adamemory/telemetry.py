import platform
import sys

import importlib
from posthog import Posthog


class AnonymousTelemetry:
    _instance = None

    @classmethod
    def get_instance(cls, **kwargs):
        if cls._instance is None:
            cls._instance = cls(**kwargs)

        return cls._instance

    def __init__(self, project_api_key, host):
        self.posthog = Posthog(project_api_key=project_api_key, host=host)

    def capture_event(self, event_name, properties=None):
        if properties is None:
            properties = {}
        properties = {
            "python-version": sys.version,
            "OS": sys.platform,
            "OS-version": platform.version(),
            "OS-release": platform.release(),
            "processor": platform.processor(),
            "machine": platform.machine(),
            "version": ".".join([str(i) for i in importlib.metadata.version("adamemory")])
            **properties,
        }
        self.posthog.capture(
            distinct_id="<TODO>", event=event_name, properties=properties
        )

    def close(self):
        self.posthog.shutdown()


# Initialize AnonymousTelemetry
telemetry = AnonymousTelemetry.get_instance(
    project_api_key="<TODO>",
    host="https://eu.i.posthog.com"
)


def capture_event(event_name, memory_instance, additional_data=None):
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
    event_data = {
        "function": f"{instance.__class__.__module__}.{instance.__class__.__name__}",
    }
    if additional_data:
        event_data.update(additional_data)

    telemetry.capture_event(event_name, event_data)