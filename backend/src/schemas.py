from typing import Optional, Dict,  List
from pydantic import BaseModel
from .engine.schemas import IRBuilderOutput, ResolverOutput

class RequestContext(BaseModel):
    description: Optional[str] = ""
    details: Optional[Dict]

class PolicySummaryRequest(BaseModel):
    message: str
    context: RequestContext

class PolicySummaryResponse(BaseModel):
    session_id: str
    summary: str

class PolicyTranslateRequest(BaseModel):
    session_id: str
    confirm: bool


class PolicyTranslateResponse(BaseModel):
    policy_id: str
    resolver_output: ResolverOutput
    ir: IRBuilderOutput
    validation_warnings: Optional[List[str]] = []
    batfish_warnings: Optional[List[Dict[str, str]]] = []  # List of { "severity": "warning"|"error", "message": "..." }
    configs: Optional[Dict[str, str]] = {}