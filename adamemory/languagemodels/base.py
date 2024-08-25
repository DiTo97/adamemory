"""
base module
"""
from typing import Optional
from abc import ABC, abstractmethod

from ..config import abc_LLMConfig


class abc_LLM(ABC):
    def __init__(self, config: Optional[abc_LLMConfig] = None):
        """Initialize a base LLM class

        :param config: LLM configuration option class, defaults to None
        :type config: Optional[BaseLlmConfig], optional
        """
        if config is None:
            self.config = abc_LLMConfig()
        else:
            self.config = config

    @abstractmethod
    def generate_response(self, messages):
        """
        Generate a response based on the given messages.

        Args:
            messages (list): List of message dicts containing 'role' and 'content'.

        Returns:
            str: The generated response.
        """
        pass