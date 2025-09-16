from typing import List, Optional
from sentence_transformers import SentenceTransformer
import httpx
from fastapi import HTTPException
from const.env_variables import OLLAMA_BASE_URL, MODEL_NAME_VAL, EMBEDDING_MODEL_NAME, OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL
from services.openAiService import open_ai_service

_model: Optional[SentenceTransformer] = None

def ensure_model_ready() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model

def embed_texts(texts: List[str], batch_size: int = 64) -> List[List[float]]:
    if not texts:
        return []
    model = ensure_model_ready()
    vectors = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=False,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return [v.tolist() for v in vectors]


def get_model_dim(use_openai: bool = False) -> int:
    if use_openai:
        return get_openai_model_dim()
    else:
        return ensure_model_ready().get_sentence_embedding_dimension()

async def generate_embedding(text: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={"model": MODEL_NAME_VAL, "prompt": text},
        )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code,
                                detail=f"Failed to generate embedding: {response.text}")
        return response.json()["embedding"]


async def generate_embedding_openai(text: str, model: str = OPENAI_EMBEDDING_MODEL):
    """
    Generate embedding using OpenAI API.
    
    Args:
        text: The text to embed
        model: The OpenAI embedding model to use (default: text-embedding-3-small)
    
    Returns:
        List[float]: The embedding vector
    """
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
    
    try:
        response = await open_ai_service.create_embedding(
            input_text=text,
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate OpenAI embedding: {str(e)}"
        )


async def embed_texts_openai(texts: List[str], model: str = OPENAI_EMBEDDING_MODEL, batch_size: int = 100) -> List[List[float]]:
    """
    Generate embeddings for multiple texts using OpenAI API with batching.
    
    Args:
        texts: List of texts to embed
        model: The OpenAI embedding model to use (default: text-embedding-3-small)
        batch_size: Number of texts to process in each batch (OpenAI supports up to 2048 inputs per request)
    
    Returns:
        List[List[float]]: List of embedding vectors
    """
    if not texts:
        return []
    
    if not OPENAI_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="OpenAI API key not configured"
        )
    
    all_embeddings = []
    
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        
        try:
            response = await open_ai_service.create_embedding(
                input_text=batch_texts,
                model=model
            )
            
            batch_embeddings = [data.embedding for data in response.data]
            all_embeddings.extend(batch_embeddings)
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate OpenAI embeddings for batch {i//batch_size + 1}: {str(e)}"
            )
    
    return all_embeddings


def get_openai_model_dim(model: str = OPENAI_EMBEDDING_MODEL) -> int:
    """
    Get the dimension of the specified OpenAI embedding model.
    
    Args:
        model: The OpenAI embedding model name
    
    Returns:
        int: The dimension of the embedding model
    """
    model_dimensions = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }
    
    if model not in model_dimensions:
        raise ValueError(f"Unknown OpenAI embedding model: {model}")
    
    return model_dimensions[model]