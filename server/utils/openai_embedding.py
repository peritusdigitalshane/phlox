"""
OpenAI embedding function for ChromaDB.
"""

import requests
import json
import logging
from typing import List, Dict, Any, Union, Optional

logger = logging.getLogger(__name__)

class OpenAIEmbeddingFunction:
    """
    OpenAI embedding function for ChromaDB that mimics the OllamaEmbeddingFunction interface.
    """
    
    def __init__(self, api_key: str, model_name: str = "text-embedding-3-small", base_url: str = "https://api.openai.com/v1"):
        """
        Initialize the OpenAIEmbeddingFunction.
        
        Args:
            api_key: The API key for the OpenAI API
            model_name: The model to use for embeddings
            base_url: The base URL for the OpenAI API
        """
        self.api_key = api_key
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def __call__(self, texts: List[str]) -> List[List[float]]:
        """
        Get embeddings for a list of texts.
        
        Args:
            texts: The texts to embed
            
        Returns:
            A list of embeddings
        """
        if not texts:
            return []
        
        try:
            # OpenAI API can handle batching, so we can send all texts at once
            response = requests.post(
                f"{self.base_url}/embeddings",
                headers=self.headers,
                json={
                    "model": self.model_name,
                    "input": texts
                }
            )
            
            if response.status_code != 200:
                logger.error(f"OpenAI API error: {response.text}")
                raise Exception(f"OpenAI API error: {response.text}")
            
            result = response.json()
            
            # Extract embeddings from the response
            embeddings = [item["embedding"] for item in result["data"]]
            
            return embeddings
        except Exception as e:
            logger.error(f"Error getting embeddings from OpenAI API: {str(e)}")
            raise
