from pydantic import BaseModel
from const.variables import qdrant_limit

class SearchQuery(BaseModel):
    query: str
    top_k: int = qdrant_limit
    collection_name: str 