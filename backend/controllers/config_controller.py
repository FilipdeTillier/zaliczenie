from fastapi import HTTPException, APIRouter
from services.qdrantService import QdrantService
import httpx
from const.env_variables import OLLAMA_BASE_URL, MODEL_NAME_VAL, OLLAMA_HOST, OLLAMA_PORT

qdrant_service = QdrantService(host=OLLAMA_HOST, port=OLLAMA_PORT)

router = APIRouter(
    prefix=""
)

@router.get("/", tags=["Health"])
async def root():
    """
    Root endpoint that returns basic API information.
    """
    return {"message": "Welcome to the RAG API", "model": MODEL_NAME_VAL}

@router.get("/health", tags=["Health"])
async def health():
    """
    Health check endpoint that verifies the status of all required services.
    
    Returns:
        - Status of the API
        - Qdrant connection status
        - Ollama connection status and available models
    """
    try:
        qdrant_collections = qdrant_service.get_collections()
        
        ollama_status = {"status": "unknown"}
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
                if resp.status_code == 200:
                    ollama_status = {"status": "connected", "models": [m["name"] for m in resp.json().get("models", [])]}
                else:
                    ollama_status = {"status": "error", "details": resp.text}
        except Exception as e:
            ollama_status = {"status": "error", "details": str(e)}
        
        return {
            "status": "healthy" if ollama_status["status"] == "connected" else "degraded", 
            "qdrant": {"status": "connected", "collections": len(qdrant_collections)},
            "ollama": ollama_status
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

