from pydantic import BaseModel

class SearchQuery(BaseModel):
    query: str
    top_k: int = 5
    collection_name: str 