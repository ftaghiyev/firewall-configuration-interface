from .gate import FirewallSafetyGate
from ..schemas import IRBuilderOutput
from typing import Tuple, List

gates = [FirewallSafetyGate()] # one gate for now, can add more later


def verify_safety(ir: IRBuilderOutput) -> Tuple[bool, List[str]]:
    all_errors = []
    
    for gate in gates:
        is_safe, errors = gate.enforce(ir)
        all_errors.extend(errors)
    
    return (len(all_errors) == 0), all_errors
