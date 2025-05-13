"""
Factory for creating LLM clients based on configuration.
"""

import logging
from typing import Union, Optional, Any

from server.utils.openai_client import AsyncClient as AsyncOpenAIClient
from server.utils.openai_client import Client as OpenAIClient
from server.utils.openai_embedding import OpenAIEmbeddingFunction
from ollama import AsyncClient as AsyncOllamaClient
from ollama import Client as OllamaClient
from chromadb.utils.embedding_functions import OllamaEmbeddingFunction

logger = logging.getLogger(__name__)

def get_async_client(config: dict) -> Union[AsyncOpenAIClient, AsyncOllamaClient]:
    """
    Get an async client based on the configuration.
    
    Args:
        config: The configuration dictionary
        
    Returns:
        An async client for the configured LLM service
    """
    # Check if OpenAI API key is configured
    if config.get("OPENAI_API_KEY") and config["OPENAI_API_KEY"] != "&nbsp;":
        logger.info("Using OpenAI client")
        return AsyncOpenAIClient(
            host=config.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=config["OPENAI_API_KEY"]
        )
    
    # Fall back to Ollama
    logger.info("Using Ollama client")
    return AsyncOllamaClient(host=config["OLLAMA_BASE_URL"])

def get_client(config: dict) -> Union[OpenAIClient, OllamaClient]:
    """
    Get a synchronous client based on the configuration.
    
    Args:
        config: The configuration dictionary
        
    Returns:
        A client for the configured LLM service
    """
    # Check if OpenAI API key is configured
    if config.get("OPENAI_API_KEY") and config["OPENAI_API_KEY"] != "&nbsp;":
        logger.info("Using OpenAI client")
        return OpenAIClient(
            host=config.get("OPENAI_BASE_URL", "https://api.openai.com/v1"),
            api_key=config["OPENAI_API_KEY"]
        )
    
    # Fall back to Ollama
    logger.info("Using Ollama client")
    return OllamaClient(host=config["OLLAMA_BASE_URL"])

def get_embedding_function(config: dict) -> Union[OpenAIEmbeddingFunction, OllamaEmbeddingFunction]:
    """
    Get an embedding function based on the configuration.
    
    Args:
        config: The configuration dictionary
        
    Returns:
        An embedding function for the configured LLM service
    """
    # Check if OpenAI API key is configured
    if config.get("OPENAI_API_KEY") and config["OPENAI_API_KEY"] != "&nbsp;":
        logger.info("Using OpenAI embedding function")
        return OpenAIEmbeddingFunction(
            api_key=config["OPENAI_API_KEY"],
            model_name=config.get("EMBEDDING_MODEL", "text-embedding-3-small"),
            base_url=config.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        )
    
    # Fall back to Ollama
    logger.info("Using Ollama embedding function")
    return OllamaEmbeddingFunction(
        url=f"{config['OLLAMA_BASE_URL']}/api/embeddings",
        model_name=config["EMBEDDING_MODEL"],
    )
