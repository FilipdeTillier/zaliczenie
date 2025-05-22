from typing import Optional, List
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class QueryPayload(BaseModel):
    model: str
    stream: bool
    messages: List[Message]

class QueryRequest(BaseModel):
    query: QueryPayload
    collection_name: Optional[str] = None
    use_rag: bool = True