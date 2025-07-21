import os
from fastapi import HTTPException, APIRouter
from models.collection import Collection
from services.qdrantService import QdrantService

qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", 6333))

qdrant_service = QdrantService(host=qdrant_host, port=qdrant_port)

router = APIRouter(
    prefix="",
    tags=[""]
)

@router.get("/collections", tags=["Collections"])
async def get_collections():
    """
    Retrieve all available collections from Qdrant.
    
    Returns:
        List of collection names
    """
    try:
        collections = qdrant_service.get_collections()
        return {"collections": [c for c in collections]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get collections: {str(e)}")
        

@router.post("/collections", tags=["Collections"])
async def create_collection(collection: Collection):
    """
    Create a new collection in Qdrant.
    
    Args:
        collection: Collection configuration including name and vector settings
        
    Returns:
        Success message with collection name
    """
    try:
        qdrant_service.create_collection(
            collection_name=collection.name,
            vector_size=collection.vector_size,
            distance=collection.distance
        )
        return {"status": "success", "message": f"Collection {collection.name} created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create collection: {str(e)}")
