import httpx
from fastapi import HTTPException
from typing import List, Dict, Any
from const.env_variables import OLLAMA_BASE_URL, OLLAMA_HOST, OLLAMA_PORT, INIT_MODEL_NAME_VAL, MODEL_NAME_VAL

class OllamaService:
    def __init__(self):
        self.ollama_host = OLLAMA_HOST
        self.ollama_port = OLLAMA_PORT
        self.base_url = f"http://{self.ollama_host}:{self.ollama_port}"
        self.model = MODEL_NAME_VAL

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

    async def query_llm(prompt: object):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/chat",
                json=prompt if isinstance(prompt, dict) else {"model": MODEL_NAME_VAL, "prompt": str(prompt)},
                timeout=120,
            )
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code,
                                    detail=f"Failed to query LLM: {response.text}")
            return response.json()
