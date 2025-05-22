from typing import Optional
from pydantic import BaseModel

class ModelPullRequest(BaseModel):
    MODEL_NAME_VAL: Optional[str] = None 