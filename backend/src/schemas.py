from typing import Optional, Dict
from pydantic import BaseModel

class RequestContext(BaseModel):
    description: Optional[str] = ""
    details: Optional[Dict]

class PolicyTranslationRequest(BaseModel):
    message: str
    context: RequestContext