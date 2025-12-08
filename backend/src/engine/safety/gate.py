from typing import List, Tuple
from .base import SafetyGate
from ..schemas import IRBuilderOutput

GLOBAL_ANY = {"any", "0.0.0.0/0", "*", "internet"}


class FirewallSafetyGate(SafetyGate):

    def enforce(self, ir: IRBuilderOutput) -> Tuple[bool, List[str]]:
        errors: List[str] = []

        if not ir.rules:
            errors.append("ERROR: No rules were generated. The policy might be invalid or empty.")
            return False, errors

        for r in ir.rules:


            # any-any allow
            if r.action == "allow":

                if any(src.lower() in GLOBAL_ANY for src in r.src) and \
                   any(dst.lower() in GLOBAL_ANY for dst in r.dst):
                    errors.append(
                        f"ERROR: Rule {r.id} allows traffic from ANY source to ANY destination."
                    )

            # missing zones
            if not r.src_zone or not r.dst_zone:
                errors.append(
                    f"ERROR: Rule {r.id} is missing source or destination zone."
                )

            # missing protocol
            if not r.protocol:
                errors.append(
                    f"ERROR: Rule {r.id} is missing protocol specification."
                )

            # empty critical fields
            if not r.src:
                errors.append(f"ERROR: Rule {r.id} has empty source list.")
            if not r.dst:
                errors.append(f"ERROR: Rule {r.id} has empty destination list.")

        is_safe = len(errors) == 0
        
        return is_safe, errors