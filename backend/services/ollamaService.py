import os
import httpx
from fastapi import HTTPException
from typing import List, Dict, Any
import json
from .modelHelpers import map_ollama_response

class OllamaService:
    def __init__(self):
        self.ollama_host = os.getenv("OLLAMA_HOST", "localhost")
        self.ollama_port = os.getenv("OLLAMA_PORT", "11434")
        self.base_url = f"http://{self.ollama_host}:{self.ollama_port}"
        self.model = os.getenv("MODEL_NAME_VAL", "deepseek-r1:7b")

    async def query_model(self, query_data) -> Dict[str, Any]:
        """
        Query the Ollama model with the given messages.
        
        Args:
            query_data: Query object containing model, messages, etc.
            
        Returns:
            Dictionary containing the model's response
        """
        try:
            if hasattr(query_data, 'dict'):
                payload = query_data.dict()
            elif hasattr(query_data, 'model_dump'):
                payload = query_data.model_dump()
            else:
                payload = query_data

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail=f"Failed to query Ollama model: {response.text}"
                    )
                
                return response.json()
                
        except httpx.TimeoutException:
            print('Timeout exception')
            raise HTTPException(
                status_code=504,
                detail="Request to Ollama model timed out"
            )
        except httpx.ConnectError:
            print('Connection error - Ollama server might not be running')
            raise HTTPException(
                status_code=503,
                detail="Cannot connect to Ollama server. Make sure Ollama is running."
            )
        except Exception as e:
            print('Error:', str(e))
            raise HTTPException(
                status_code=500,
                detail=f"Error querying Ollama model: {str(e)}"
            )

    def _format_messages(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Format messages to match Ollama's expected format.
        """
        return messages