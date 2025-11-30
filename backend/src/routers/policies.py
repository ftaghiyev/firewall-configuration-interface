from fastapi import APIRouter, Response
from .. import schemas
from ..engine.agents import summarize_intent, resolve_policy, build_ir
from ..engine.validator.palo_alto import PaloAltoLinter
from ..engine.batfish.validator import BatfishManager
from ..engine.compiler.palo_alto import PaloAltoCompiler
import uuid

router = APIRouter(
    prefix="/policies",
    tags=["policies"])

# temporary in-memory confirm cache (will be replaced with proper DB later)
CONFIRM_CACHE = {}
POLICIES_CACHE = {}

@router.post("/confirm", response_model = schemas.PolicySummaryResponse)
def confirm_policy(request: schemas.PolicySummaryRequest):

    message = request.message
    context = request.context.model_dump()

    summary = summarize_intent(
        nl_policy=message,
        context=context
    )

    session_id = str(uuid.uuid4())
    CONFIRM_CACHE[session_id] = {
        "message": message,
        "context": context
    }

    return schemas.PolicySummaryResponse(session_id=session_id, summary=summary)


@router.post("/translate", response_model = schemas.PolicyTranslateResponse)
def translate_policy(payload: schemas.PolicyTranslateRequest):

    session_id = payload.session_id
    confirm = payload.confirm  # will be ignored for now 

    if session_id not in CONFIRM_CACHE:
        return Response(status_code=404, content="Session ID not found")
    

    cached = CONFIRM_CACHE[session_id]

    resolved = resolve_policy(
        nl_policy=cached["message"],
        context=cached["context"]
    )

    print("Resolved Policy:", resolved)

    ir_result = build_ir(
        resolver_output=resolved,
        context=cached["context"]
    )

    print("Intermediate Representation:", ir_result)


    policy_id = str(uuid.uuid4())
    

    POLICIES_CACHE[policy_id] = {
        "session_id": session_id,
        "ir": ir_result
    }



    validator = PaloAltoLinter()
    valid, warnings = validator.validate(ir_result)
    if not valid:
        print("Validation Warnings:", warnings)


    palo_alto_compiler = PaloAltoCompiler()
    palo_alto_config = palo_alto_compiler.compile_policy(ir_result)
    
    # Batfish Validation
    batfish_manager = BatfishManager()
    bf_warnings = batfish_manager.validate(palo_alto_config, context=cached["context"])
    

    return schemas.PolicyTranslateResponse(
        policy_id = policy_id,
        resolver_output = resolved,
        ir = ir_result,
        validation_warnings = warnings,
        batfish_warnings = bf_warnings,
        configs = {"palo_alto": palo_alto_config}
    )
