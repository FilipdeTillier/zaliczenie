from openai import OpenAI
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv


load_dotenv()

class OpenAIService:
    def __init__(self):
        self.service = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def query_model(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        try:

            response = self.service.responses.create(
                model=model,
                input=messages
            )

            return response
            
        except Exception as e:
            raise Exception(f"Error querying OpenAI API: {str(e)}") 

    async def create_embedding(
        self,
        input_text: str,
        model: str = "text-embedding-ada-002",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create embeddings for the provided input text using the specified model.
        """
        try:
            response = self.service.embeddings.create(
                input=input_text,
                model=model,
                **kwargs
            )
            return response
        except Exception as e:
            raise Exception(f"Error creating embedding with OpenAI API: {str(e)}")

open_ai_service = OpenAIService()