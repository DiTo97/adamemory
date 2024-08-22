from typing import Optional
from abc import ABC, abstractmethod

from ..config import abc_EmbeddingConfig


class abc_Embedding(ABC):
    """Initialized a base embedding class

    :param config: Embedding configuration option class, defaults to None
    :type config: Optional[BaseEmbedderConfig], optional
    """

    def __init__(self, config: Optional[abc_EmbeddingConfig] = None):
        if config is None:
            self.config = abc_EmbeddingConfig()
        else:
            self.config = config

    @abstractmethod
    def embed(self, text):
        """
        Get the embedding for the given text.

        Args:
            text (str): The text to embed.

        Returns:
            list: The embedding vector.
        """
        pass