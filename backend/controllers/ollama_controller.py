import os
from fastapi import HTTPException, APIRouter, Body, Query
from services.qdrantService import QdrantService
import httpx
from fastapi.responses import StreamingResponse
from models.model_pull_request import ModelPullRequest
from const.env_variables import OLLAMA_BASE_URL, OLLAMA_HOST, OLLAMA_PORT, INIT_MODEL_NAME_VAL

qdrant_service = QdrantService(host=OLLAMA_HOST, port=OLLAMA_PORT)

router = APIRouter(
    prefix="",
    tags=[""]
)

async def pull_model(INIT_MODEL_NAME_VAL: str = INIT_MODEL_NAME_VAL):
    """Pull a model with timeout handling"""
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{OLLAMA_BASE_URL}/api/pull",
                json={"name": INIT_MODEL_NAME_VAL}
            )
            if response.status_code != 200:
                print(f"Failed to pull model {INIT_MODEL_NAME_VAL}: {response.text}")
                return False
            return True
    except httpx.TimeoutException:
        print(f"Timeout while pulling model {INIT_MODEL_NAME_VAL}")
        return False
    except Exception as e:
        print(f"Error pulling model {INIT_MODEL_NAME_VAL}: {str(e)}")
        return False


@router.get("/search_model", tags=["Models"])
async def search_model(
    search: str = Query(None, description="Search for models by name or description."),
    model_identifier: str = Query(None, description="Filter models by identifier."),
    namespace: str = Query(None, description="Filter models by namespace."),
    capability: str = Query(None, description="Filter models by capability."),
    model_type: str = Query(None, description="Filter models by type. Valid values: official, community."),
    sort_by: str = Query(None, description="Sort the results by a specific field. Valid fields: pulls, last_updated."),
    order: str = Query(None, description="Sort order. Valid values: asc, desc."),
    limit: int = Query(20, description="Number of results to return. Default is 20."),
    skip: int = Query(0, description="Number of results to skip. Default is 0."),
):
    """
    Search for models from the OllamaDB public model registry.

    Returns:
        List of models and metadata from https://ollamadb.dev/api/v1/models
    """
    url = "https://ollamadb.dev/api/v1/models"
    params = {}
    if search is not None:
        params["search"] = search
    if model_identifier is not None:
        params["model_identifier"] = model_identifier
    if namespace is not None:
        params["namespace"] = namespace
    if capability is not None:
        params["capability"] = capability
    if model_type is not None:
        params["model_type"] = model_type
    if sort_by is not None:
        params["sort_by"] = sort_by
    if order is not None:
        params["order"] = order
    if limit is not None:
        params["limit"] = limit
    if skip is not None:
        params["skip"] = skip

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                return resp.json()
            else:
                return {
                    "status_code": resp.status_code,
                    "error": resp.text
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search models: {str(e)}")


@router.post("/api/pull", tags=["Models"])
async def pull_model_endpoint(
    model: str = Body(..., embed=True, description="Name of the model to pull"),
    insecure: bool = Body(False, embed=True, description="Allow insecure connections to the library. Only use this if you are pulling from your own library during development."),
    stream: bool = Body(True, embed=True, description="If false, the response will be returned as a single response object, rather than a stream of objects")
):
    """
    Pull a model from the Ollama library.

    Downloads a model from the Ollama library. Cancelled pulls are resumed from where they left off, and multiple calls will share the same download progress.

    Args:
        model: Name of the model to pull (required)
        insecure: Allow insecure connections to the library (optional)
        stream: If false, the response will be returned as a single response object, rather than a stream of objects (optional)

    Returns:
        Streaming JSON objects with pull progress, or a single JSON object if stream is false.
    """
    url = f"{OLLAMA_BASE_URL}/api/pull"
    payload = {
        "model": model,
        "insecure": insecure,
        "stream": stream
    }

    async def stream_response():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("POST", url, json=payload) as response:
                async for line in response.aiter_lines():
                    if line.strip():
                        yield line + "\n"

    try:
        if stream:
            return StreamingResponse(stream_response(), media_type="application/json")
        else:
            async with httpx.AsyncClient(timeout=None) as client:
                resp = await client.post(url, json=payload)
                return resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to pull model: {str(e)}")


@router.get("/models", tags=["Models"])
async def get_models():
    """
    Retrieve all available models from Ollama.
    
    Returns:
        List of available models
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            if resp.status_code == 200:
                models = resp.json()
                return {"models": models.get("models", [])}
            else:
                raise HTTPException(status_code=resp.status_code, detail="Failed to get models from Ollama")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")

@router.post("/pull_model", tags=["Models"])
async def start_model_pull(request: ModelPullRequest):
    """
    Pull a model from Ollama with timeout handling.
    
    Args:
        request: Model pull request configuration
        
    Returns:
        Success or error message with model name
    """
    INIT_MODEL_NAME_VAL = request.INIT_MODEL_NAME_VAL or 'INIT_MODEL_NAME_VAL'
    success = await pull_model(INIT_MODEL_NAME_VAL)
    
    if success:
        return {"status": "success", "message": f"Model {INIT_MODEL_NAME_VAL} pulled successfully"}
    else:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to pull model {INIT_MODEL_NAME_VAL} - operation timed out or failed"
        )

@router.get("/model_status", tags=["Models"])
async def model_status():
    """
    Get the current status of model operations.
    
    Returns:
        Current model status
    """
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/status")
            if resp.status_code == 200:
                return resp.json()
            else:
                return {"status": "unknown"}
    except Exception:
        return {"status": "unknown"}
