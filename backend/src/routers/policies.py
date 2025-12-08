from ..engine.safety.runner import verify_safety
from fastapi import APIRouter, Response
from .. import schemas
from ..engine.agents import summarize_intent, resolve_policy, build_ir
from ..engine.linter.runner import lint_ir_all
from ..engine.batfish.validator import BatfishManager
from ..engine.compiler.runner import compile_ir_all
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
    
    # Retrieve cached data
    cached = CONFIRM_CACHE[session_id]

    # Resolve Policy
    resolved = resolve_policy(
        nl_policy=cached["message"],
        context=cached["context"]
    )

    print("Resolved Policy:", resolved)

    # Build Intermediate Representation
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
    
    # Linting
    all_valid, linting_warnings = lint_ir_all(ir_result)
    if not all_valid:
        print("Linting Warnings:", linting_warnings)

    # Safety Verification
    is_safe, safety_warnings = verify_safety(ir_result)
    if not is_safe:
        print("Safety Errors:", safety_warnings)
        return schemas.PolicyTranslateResponse(
            policy_id = policy_id,
            resolver_output = resolved,
            ir = ir_result,
            linting_warnings = linting_warnings if not all_valid else {},
            safety_warnings = safety_warnings,
            configs = {"error": "Compilation skipped due to safety violations."},
            batfish_warnings = {"error": [{"severity": "error", "message": "Batfish validation skipped due to safety violations."}]}
        )

    # Compilation
    compiled_outputs = compile_ir_all(ir_result)
    
    # Batfish Validation
    bf_warnings_all = {}
    for vendor, config in compiled_outputs.items():

        batfish_manager = BatfishManager()
        bf_warnings = batfish_manager.validate(config, context=cached["context"])

        bf_warnings_all[vendor] = bf_warnings


    return schemas.PolicyTranslateResponse(
        policy_id = policy_id,
        resolver_output = resolved,
        ir = ir_result,
        linting_warnings = linting_warnings if not all_valid else {},
        safety_warnings = safety_warnings,
        configs = compiled_outputs,
        batfish_warnings = bf_warnings_all
    )
