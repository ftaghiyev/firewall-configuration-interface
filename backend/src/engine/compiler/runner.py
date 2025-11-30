from .palo_alto import PaloAltoCompiler
from ..schemas import IRBuilderOutput
from typing import Dict


VENDOR_COMPILERS_MAP = {
    "palo_alto": PaloAltoCompiler,
}


def compile_ir(ir: IRBuilderOutput, vendor: str) -> str:

    if vendor not in VENDOR_COMPILERS_MAP:
        raise ValueError(f"Unsupported vendor: {vendor}")
    
    compiler_class = VENDOR_COMPILERS_MAP[vendor]
    compiler = compiler_class()
    compiled_output = compiler.compile_policy(ir)
    
    return compiled_output


def compile_ir_all(ir: IRBuilderOutput) -> Dict[str, str]:
    compiled_outputs = {}

    for vendor, compiler_class in VENDOR_COMPILERS_MAP.items():
        compiler = compiler_class()
        compiled_output = compiler.compile_policy(ir)
        compiled_outputs[vendor] = compiled_output

    return compiled_outputs

