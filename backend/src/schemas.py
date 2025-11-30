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
    linting_warnings: Optional[Dict[str, List[str]]] = {}
    safety_warnings: Optional[List[str]] = []
    configs: Optional[Dict[str, str]] = {}
    batfish_warnings: Optional[Dict[str, List[Dict[str, str]]]] = {}  # Dictionary of vendor to list of { "severity": "warning"|"error", "message": "..." }
