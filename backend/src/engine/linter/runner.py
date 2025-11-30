from .general import GeneralIRLinter
from .palo_alto import PaloAltoLinter

LINTERS = {
    "palo_alto": [GeneralIRLinter(), PaloAltoLinter()],
}

def lint_ir(ir, vendor: str):
    all_warnings = []

    for l in LINTERS[vendor]:
        _, warnings = l.lint(ir)
        all_warnings.extend(warnings)
    return (len(all_warnings) == 0), all_warnings


def lint_ir_all(ir):
    all_warnings = {}

    all_valid = True
    for vendor in LINTERS.keys():
        is_valid, vendor_warnings = lint_ir(ir, vendor)
        all_warnings[vendor] = vendor_warnings

        if not is_valid:
            all_valid = False

    return all_valid, all_warnings