"""
openai module for embeddings
"""
import os
from typing import Optional
from ..clients.openai import OpenAIClient
from ..config import abc_EmbeddingConfig
from .base import abc_Embedding


class OpenAIEmbedding(abc_Embedding):
    """
    OpenAI embedding implementation.

    :param config: Embedding configuration option class, defaults to None
    :type config: Optional[abc_EmbeddingConfig], optional
    """

    def __init__(self, config: Optional[abc_EmbeddingConfig] = None):
        """
        Initializes the OpenAIEmbedding instance.

        :param config: Embedding configuration option class, defaults to None
        :type config: Optional[abc_EmbeddingConfig], optional
        """
        super().__init__(config)

        self.config.model = self.config.model or "text-embedding-3-small"
        self.config.embedding_dims = self.config.embedding_dims or 1536

        api_key = os.getenv("OPENAI_API_KEY") or self.config.api_key
        self.client = OpenAIClient.get_instance(api_key=api_key)

    def embed(self, text):
        """
        Get the embedding for the given text using OpenAI.

        Args:
            text (str): The text to embed.

        Returns:
            list: The embedding vector.
        """
        text = text.replace("\n", " ")
        return (
            self.client.embeddings.create(input=[text], model=self.config.model)
            .data[0]
            .embedding
        )
