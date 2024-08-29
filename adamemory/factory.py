"""
factory module
"""
import importlib

from .config import abc_EmbeddingConfig, abc_LLMConfig

def load_class(class_type):
    """
    Loads a class dynamically from a given module path and class name.

    :param class_type: The full path to the class in the format 'module_path.class_name'
    :type class_type: str
    :return: The loaded class
    :rtype: type
    """
    module_path, class_name = class_type.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)

class LlmFactory:
    """
    Factory class for creating LLM instances.
    """
    provider_to_class = {
        "openai": "adamemory.languagemodels.openai.OpenAILLM",
    }

    @classmethod
    def create(cls, provider_name, config):
        """
        Creates an LLM instance based on the provider name and configuration.

        :param provider_name: The name of the LLM provider
        :type provider_name: str
        :param config: The configuration for the LLM
        :type config: dict
        :return: An instance of the LLM
        :rtype: object
        :raises ValueError: If the provider is unsupported
        """
        class_type = cls.provider_to_class.get(provider_name)
        if class_type:
            llm_instance = load_class(class_type)
            base_config = abc_LLMConfig(**config)
            return llm_instance(base_config)
        else:
            raise ValueError(f"Unsupported Llm provider: {provider_name}")

class EmbedderFactory:
    """
    Factory class for creating Embedder instances.
    """
    provider_to_class = {
        "openai": "adamemory.embeddings.openai.OpenAIEmbedding",
    }

    @classmethod
    def create(cls, provider_name, config):
        """
        Creates an Embedder instance based on the provider name and configuration.

        :param provider_name: The name of the Embedder provider
        :type provider_name: str
        :param config: The configuration for the Embedder
        :type config: dict
        :return: An instance of the Embedder
        :rtype: object
        :raises ValueError: If the provider is unsupported
        """
        class_type = cls.provider_to_class.get(provider_name)
        if class_type:
            embedder_instance = load_class(class_type)
            base_config = abc_EmbeddingConfig(**config)
            return embedder_instance(base_config)
        else:
            raise ValueError(f"Unsupported Embedder provider: {provider_name}")
