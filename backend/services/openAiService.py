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
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "stream": stream,
            }
            
            if max_tokens is not None:
                params["max_tokens"] = max_tokens
                
            params.update(kwargs)
            
            response = self.service.chat.completions.create(**params)
            
            # return map_ollama_response(response)
            return response
            # return {
            #     "id": response.id,
            #     "model": response.model,
            #     "created": response.created,
            #     "choices": [
            #         {
            #             "message": {
            #                 "role": choice.message.role,
            #                 "content": choice.message.content
            #             },
            #             "finish_reason": choice.finish_reason
            #         }
            #         for choice in response.choices
            #     ],
            #     "usage": {
            #         "prompt_tokens": response.usage.prompt_tokens,
            #         "completion_tokens": response.usage.completion_tokens,
            #         "total_tokens": response.usage.total_tokens
            #     }
            # }
            
        except Exception as e:
            raise Exception(f"Error querying OpenAI API: {str(e)}") 