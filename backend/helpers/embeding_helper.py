from typing import List, Optional
from sentence_transformers import SentenceTransformer
import httpx
from fastapi import HTTPException
from const.env_variables import OLLAMA_BASE_URL, MODEL_NAME_VAL, EMBEDDING_MODEL_NAME

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


def get_model_dim() -> int:
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