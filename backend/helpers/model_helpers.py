from typing import Dict, Any
from datetime import datetime

def map_openai_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maps OpenAI response to standardized format.
    Since OpenAI response already matches our target format, we just need to wrap it.
    """
    return {
        "response": response,
        "source_documents": []
    }

def map_ollama_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maps Ollama response to standardized format matching OpenAI structure.
    """
    created_at = datetime.fromisoformat(response["created_at"].replace("Z", "+00:00"))
    created_timestamp = int(created_at.timestamp())

    standardized_response = {
        "id": None,
        "model": response["model"],
        "created": created_timestamp,
        "choices": [
            {
                "message": {
                    "role": response["message"]["role"],
                    "content": response["message"]["content"]
                },
                "finish_reason": response["done_reason"]
            }
        ],
        "usage": {
            "prompt_tokens": response["prompt_eval_count"],
            "completion_tokens": response["eval_count"],
            "total_tokens": response["prompt_eval_count"] + response["eval_count"]
        }
    }

    return {
        "response": standardized_response,
        "source_documents": []
    }

def standardize_response(response: Dict[str, Any], provider: str) -> Dict[str, Any]:
    """
    Main function to standardize responses from different AI providers.
    
    Args:
        response: The raw response from the AI provider
        provider: The provider name ("openai" or "ollama")
    
    Returns:
        Dict containing standardized response format
    """
    if provider.lower() == "openai":
        return map_openai_response(response)
    elif provider.lower() == "ollama":
        return map_ollama_response(response)
    else:
        raise ValueError(f"Unsupported provider: {provider}") 