from .base import VendorCompiler
from typing import List

class PaloAltoCompiler(VendorCompiler):

    def _fmt(self, x: str) -> str:
        """Quote names containing spaces or special chars."""
        if " " in x or "-" in x:
            return f'"{x}"'
        return x

    def _service_name(self, ir_rule) -> str:
        """Return a valid PAN-OS service or application."""
        proto = ir_rule.protocol.lower()

        if proto in ["any", "icmp"]:
            return "application-default"

        if proto == "tcp" and ir_rule.dst_ports == [443]:
            return "application-default"
        
        # Guard against empty ports list which can happen if LLM produces invalid IR
        # or for certain protocols. Fallback to app-default.
        if not ir_rule.dst_ports:
             return "application-default"

        port = ir_rule.dst_ports[0]
        return f"{proto}_{port}"


    def compile_rule(self, ir_rule) -> str:
        name = self._fmt(ir_rule.id)

        src_zone = self._fmt(ir_rule.src_zone)
        dst_zone = self._fmt(ir_rule.dst_zone)

        src_list = " ".join(self._fmt(x) for x in ir_rule.src)
        dst_list = " ".join(self._fmt(x) for x in ir_rule.dst)

        service = self._service_name(ir_rule)

        lines: List[str] = []

        base = f"set rulebase security rules {name}"

        lines.append(f"{base} from {src_zone}")
        lines.append(f"{base} to {dst_zone}")
        lines.append(f"{base} source {src_list}")
        lines.append(f"{base} destination {dst_list}")
        lines.append(f"{base} service {service}")
        lines.append(f"{base} action {ir_rule.action}")

        if ir_rule.log:
            lines.append(f"{base} log-start yes")
            lines.append(f"{base} log-end yes")

        if ir_rule.schedule:
            sch = self._fmt(ir_rule.schedule)
            lines.append(f"{base} schedule {sch}")

        return "\n".join(lines)

    def compile_policy(self, ir_policy) -> str:
        """Compile entire IR rule list into a single CLI text."""
        rule_texts = [self.compile_rule(rule) for rule in ir_policy.rules]
        return "\n\n".join(rule_texts)
