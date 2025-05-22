from pydantic import BaseModel

class Collection(BaseModel):
    name: str
    vector_size: int = 1024
    distance: str = "Cosine"
