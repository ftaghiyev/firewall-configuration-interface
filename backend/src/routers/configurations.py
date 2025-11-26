from fastapi import APIRouter
from .. import schemas
from ..firewall_agents import summarize_intent
import uuid

router = APIRouter(
    prefix="/policies",
    tags=["policies"])

# temporary in-memory confirm cache (will be replaced with proper DB later)
CONFIRM_CACHE = {}


@router.post("/confirm", response_model = dict )
def confirm_policy(request: schemas.PolicyTranslationRequest):

    message = request.message
    context = request.context

    summary = summarize_intent(
        nl_policy=message,
        context=context
    )

    session_id = str(uuid.uuid4())
    CONFIRM_CACHE[session_id] = {
        "message": message,
        "context": context
    }

    return {"session_id": session_id, "summary": summary}


