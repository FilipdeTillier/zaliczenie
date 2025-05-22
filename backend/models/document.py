from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class Document(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = None