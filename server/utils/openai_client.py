"""
OpenAI client implementation that mimics the Ollama client interface.
This allows for easier migration from Ollama to OpenAI.
"""

import aiohttp
import json
import logging
from typing import Dict, List, Any, Optional, Union

logger = logging.getLogger(__name__)

class AsyncClient:
    """
    Asynchronous OpenAI client that mimics the Ollama AsyncClient interface.
    """
    
    def __init__(self, host: str = "https://api.openai.com/v1", api_key: str = None):
        """
        Initialize the AsyncClient.
        
        Args:
            host: The base URL for the OpenAI API
            api_key: The API key for the OpenAI API
        """
        self.host = host.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    async def chat(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        options: Optional[Dict[str, Any]] = None,
        format: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to the OpenAI API.
        
        Args:
            model: The model to use
            messages: The messages to send
            options: Additional options for the request
            format: Response format specification
            tools: Tools available to the model
            
        Returns:
            The response from the API
        """
        options = options or {}
        
        # Map Ollama options to OpenAI parameters
        request_data = {
            "model": model,
            "messages": messages,
            "temperature": options.get("temperature", 0.7),
            "max_tokens": options.get("num_predict", None),
        }
        
        # Add response format if specified
        if format:
            request_data["response_format"] = {"type": "json_object"}
        
        # Add tools if specified
        if tools:
            request_data["tools"] = tools
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.host}/chat/completions",
                    headers=self.headers,
                    json=request_data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {error_text}")
                        raise Exception(f"OpenAI API error: {error_text}")
                    
                    result = await response.json()
                    
                    # Convert OpenAI response format to Ollama format
                    return {
                        "model": model,
                        "message": {
                            "role": "assistant",
                            "content": result["choices"][0]["message"]["content"]
                        },
                        "tool_calls": result["choices"][0]["message"].get("tool_calls", []),
                        "done": True
                    }
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise

    async def embeddings(self, model: str, prompt: str) -> Dict[str, Any]:
        """
        Get embeddings for a text prompt.
        
        Args:
            model: The model to use
            prompt: The text to embed
            
        Returns:
            The embeddings response
        """
        request_data = {
            "model": model,
            "input": prompt
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.host}/embeddings",
                    headers=self.headers,
                    json=request_data
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenAI API error: {error_text}")
                        raise Exception(f"OpenAI API error: {error_text}")
                    
                    result = await response.json()
                    
                    # Convert OpenAI response format to Ollama format
                    return {
                        "embedding": result["data"][0]["embedding"]
                    }
        except Exception as e:
            logger.error(f"Error getting embeddings from OpenAI API: {str(e)}")
            raise

class Client:
    """
    Synchronous OpenAI client that mimics the Ollama Client interface.
    """
    
    def __init__(self, host: str = "https://api.openai.com/v1", api_key: str = None):
        """
        Initialize the Client.
        
        Args:
            host: The base URL for the OpenAI API
            api_key: The API key for the OpenAI API
        """
        self.host = host.rstrip('/')
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def chat(
        self, 
        model: str, 
        messages: List[Dict[str, str]], 
        options: Optional[Dict[str, Any]] = None,
        format: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to the OpenAI API.
        
        Args:
            model: The model to use
            messages: The messages to send
            options: Additional options for the request
            format: Response format specification
            tools: Tools available to the model
            
        Returns:
            The response from the API
        """
        import requests
        
        options = options or {}
        
        # Map Ollama options to OpenAI parameters
        request_data = {
            "model": model,
            "messages": messages,
            "temperature": options.get("temperature", 0.7),
            "max_tokens": options.get("num_predict", None),
        }
        
        # Add response format if specified
        if format:
            request_data["response_format"] = {"type": "json_object"}
        
        # Add tools if specified
        if tools:
            request_data["tools"] = tools
        
        try:
            response = requests.post(
                f"{self.host}/chat/completions",
                headers=self.headers,
                json=request_data
            )
            
            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.text}")
                raise Exception(f"OpenAI API error: {response.text}")
            
            result = response.json()
            
            # Convert OpenAI response format to Ollama format
            return {
                "model": model,
                "message": {
                    "role": "assistant",
                    "content": result["choices"][0]["message"]["content"]
                },
                "tool_calls": result["choices"][0]["message"].get("tool_calls", []),
                "done": True
            }
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {str(e)}")
            raise
