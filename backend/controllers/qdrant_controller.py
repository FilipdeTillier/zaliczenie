import os
from fastapi import HTTPException, APIRouter
from models.collection import Collection
from services.qdrantService import QdrantService

# Determine embedding dimensionality from the TextEmbedding model. If the model
# or dependency isn't available (e.g. during tests without the optional
# package), fall back to the previous default size so the application remains
# functional.
try:
    from fastembed import TextEmbedding

    _embedding_model = TextEmbedding()
    _embedding_dim = len(next(_embedding_model.embed(["dimension check"])))
except Exception:
    _embedding_dim = 768

qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", 6333))

qdrant_service = QdrantService(
    host=qdrant_host, port=qdrant_port, vector_size=_embedding_dim
)

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
