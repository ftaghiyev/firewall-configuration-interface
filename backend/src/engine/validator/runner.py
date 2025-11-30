from .general import GeneralIRLinter
from .palo_alto import PaloAltoLinter

VALIDATORS = {
    "palo_alto": [GeneralIRLinter(), PaloAltoLinter()],
}

def validate_ir(ir, vendor: str):
    all_warnings = []
    for v in VALIDATORS[vendor]:
        _, warnings = v.validate(ir)
        all_warnings.extend(warnings)
    return (len(all_warnings) == 0), all_warnings