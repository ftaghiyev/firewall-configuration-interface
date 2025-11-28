from typing import List, Tuple
from .base import IRValidator
from ..schemas import IRBuilderOutput


class GeneralIRValidator(IRValidator):

    def validate(self, ir: IRBuilderOutput) -> Tuple[bool, List[str]]:
        warnings: List[str] = []
        rule_ids = set()

        for r in ir.rules:
            if r.id in rule_ids:
                warnings.append(f"Duplicate rule ID: {r.id}")
            rule_ids.add(r.id)


            if not r.src:
                warnings.append(f"Rule {r.id}: source list is empty.")

            if not r.dst:
                warnings.append(f"Rule {r.id}: destination list is empty.")

            for p in r.dst_ports:
                if not (1 <= p <= 65535):
                    warnings.append(f"Rule {r.id}: invalid port {p}.")

            if r.protocol in ["icmp", "any"] and r.dst_ports:
                warnings.append(
                    f"Rule {r.id}: protocol '{r.protocol}' should not have ports."
                )

            if r.action not in ["allow", "deny"]:
                warnings.append(f"Rule {r.id}: unknown action '{r.action}'.")

            if r.direction not in [None, "inbound", "outbound", "any"]:
                warnings.append(f"Rule {r.id}: invalid direction '{r.direction}'.")

            if r.priority not in [10, 100]:
                warnings.append(
                    f"Rule {r.id}: invalid priority '{r.priority}' (should be 10 or 100)."
                )

        return (len(warnings) == 0), warnings