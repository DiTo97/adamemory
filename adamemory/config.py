"""
config module
"""
import os
from abc import ABC
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, model_validator


class Neo4jConfig(BaseModel):
    """
    Configuration for Neo4j graph database.
    """
    url: Optional[str] = Field(None, description="Host address for the graph database")
    username: Optional[str] = Field(None, description="Username for the graph database")
    password: Optional[str] = Field(None, description="Password for the graph database")

    @model_validator(mode="before")
    def check_host_port_or_path(cls, values):
        url, username, password = (
            values.get("url"),
            values.get("username"),
            values.get("password"),
        )
        if not url and not username and not password:
            raise ValueError("Please provide 'url', 'username' and 'password'.")
        return values


class GraphStoreConfig(BaseModel):
    """
    Configuration for the graph store.
    """
    provider: str = Field(default="neo4j", description="Provider of the data store")
    config: Neo4jConfig = Field(
        default_factory=Neo4jConfig,
        description="Configuration for the specific data store",
    )


class MemoryItem(BaseModel):
    """
    Represents a memory item with associated metadata.
    """
    id: str = Field(..., description="The unique identifier for the text data")
    memory: str = Field(..., description="The memory deduced from the text data")
    hash: Optional[str] = Field(None, description="The hash of the memory")
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Additional metadata for the text data"
    )
    score: Optional[float] = Field(
        None, description="The score associated with the text data"
    )
    created_at: Optional[str] = Field(
        None, description="The timestamp when the memory was created"
    )
    updated_at: Optional[str] = Field(
        None, description="The timestamp when the memory was updated"
    )


class MemoryConfig(BaseModel):
    """
    Configuration for the memory system.
    """
    vector_store: Any = Field(
        default_factory=dict, description="Configuration for the vector store"
    )
    llm: Any = Field(
        default_factory=dict, description="Configuration for the language model"
    )
    embedder: Any = Field(
        default_factory=dict, description="Configuration for the embedding model"
    )
    history_db_path: str = Field(
        default=os.path.join("mem0", "history.db"),
        description="Path to the history database",
    )
    graph_store: GraphStoreConfig = Field(
        default_factory=GraphStoreConfig, description="Configuration for the graph"
    )
    version: str = Field(default="v1.0", description="The version of the API")


class abc_LLMConfig(ABC):
    """
    Config for LLMs.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        temperature: float = 0,
        api_key: Optional[str] = None,
        max_tokens: int = 3000,
        top_p: float = 0,
        top_k: int = 1,
        # Openrouter specific
        models: Optional[list[str]] = None,
        route: Optional[str] = "fallback",
        openrouter_base_url: Optional[str] = "https://openrouter.ai/api/v1",
        site_url: Optional[str] = None,
        app_name: Optional[str] = None,
        # Ollama specific
        ollama_base_url: Optional[str] = None,
    ):
        """
        Initializes a configuration class instance for the LLM.

        :param model: Controls the OpenAI model used, defaults to None
        :type model: Optional[str], optional
        :param temperature:  Controls the randomness of the model's output.
        Higher values (closer to 1) make output more random, lower values make it more deterministic, defaults to 0
        :type temperature: float, optional
        :param api_key: OpenAI API key to be use, defaults to None
        :type api_key: Optional[str], optional
        :param max_tokens: Controls how many tokens are generated, defaults to 3000
        :type max_tokens: int, optional
        :param top_p: Controls the diversity of words. Higher values (closer to 1) make word selection more diverse,
        defaults to 1
        :type top_p: float, optional
        :param top_k: Controls the diversity of words. Higher values make word selection more diverse, defaults to 0
        :type top_k: int, optional
        :param models: Openrouter models to use, defaults to None
        :type models: Optional[list[str]], optional
        :param route: Openrouter route to be used, defaults to "fallback"
        :type route: Optional[str], optional
        :param openrouter_base_url: Openrouter base URL to be use, defaults to "https://openrouter.ai/api/v1"
        :type openrouter_base_url: Optional[str], optional
        :param site_url: Openrouter site URL to use, defaults to None
        :type site_url: Optional[str], optional
        :param app_name: Openrouter app name to use, defaults to None
        :type app_name: Optional[str], optional
        :param ollama_base_url: The base URL of the LLM, defaults to None
        :type ollama_base_url: Optional[str], optional
        """

        self.model = model
        self.temperature = temperature
        self.api_key = api_key
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.top_k = top_k

        # Openrouter specific
        self.models = models
        self.route = route
        self.openrouter_base_url = openrouter_base_url
        self.site_url = site_url
        self.app_name = app_name

        # Ollama specific
        self.ollama_base_url = ollama_base_url


class abc_EmbeddingConfig(ABC):
    """
    Config for Embeddings.
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        embedding_dims: Optional[int] = None,
        # Ollama specific
        ollama_base_url: Optional[str] = None,
        # Huggingface specific
        model_kwargs: Optional[dict] = None,
    ):
        """
        Initializes a configuration class instance for the Embeddings.

        :param model: Embedding model to use, defaults to None
        :type model: Optional[str], optional
        :param api_key: API key to be use, defaults to None
        :type api_key: Optional[str], optional
        :param embedding_dims: The number of dimensions in the embedding, defaults to None
        :type embedding_dims: Optional[int], optional
        :param ollama_base_url: Base URL for the Ollama API, defaults to None
        :type ollama_base_url: Optional[str], optional
        :param model_kwargs: key-value arguments for the huggingface embedding model, defaults a dict inside init
        :type model_kwargs: Optional[Dict[str, Any]], defaults a dict inside init

        """

        self.model = model
        self.api_key = api_key
        self.embedding_dims = embedding_dims

        # Ollama specific
        self.ollama_base_url = ollama_base_url

        # Huggingface specific
        self.model_kwargs = model_kwargs or {}
