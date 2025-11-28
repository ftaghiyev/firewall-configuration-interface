from typing import List, Tuple
from .base import IRValidator
from ..schemas import IRBuilderOutput
import ipaddress


WELL_KNOWN_DEFAULT_SERVICES = {
    ("tcp", 443): "ssl",
    ("tcp", 80): "web-browsing",
    ("udp", 53): "dns",
    ("tcp", 22): "ssh",
    ("tcp", 25): "smtp",
}

VALID_PROTOCOLS = {"tcp", "udp", "icmp", "any"}

INVALID_NAME_CHARS = set(" /\\;")


def _is_ip_or_cidr(value: str) -> bool:
    try:
        ipaddress.ip_network(value, strict=False)
        return True
    except ValueError:
        return False


class PaloAltoValidator(IRValidator):

    def validate(self, ir: IRBuilderOutput) -> Tuple[bool, List[str]]:
        warnings: List[str] = []

        for r in ir.rules:
            proto = r.protocol.lower()

            if proto not in VALID_PROTOCOLS:
                warnings.append(f"Rule {r.id}: invalid protocol '{r.protocol}'.")

            if not r.src_zone:
                warnings.append(f"Rule {r.id}: src_zone missing.")

            if not r.dst_zone:
                warnings.append(f"Rule {r.id}: dst_zone missing.")

            if r.schedule:
                if any(c in INVALID_NAME_CHARS for c in r.schedule):
                    warnings.append(
                        f"Rule {r.id}: schedule name '{r.schedule}' contains invalid PAN-OS characters."
                    )

                if r.action == "deny":
                    warnings.append(
                        f"Rule {r.id}: schedule on DENY rule is unusual in PAN-OS."
                    )

            if proto == "icmp" and r.dst_ports:
                warnings.append(
                    f"Rule {r.id}: ICMP rules cannot specify destination ports."
                )

            if proto == "any" and r.dst_ports:
                warnings.append(
                    f"Rule {r.id}: protocol 'any' should not specify ports."
                )

            if proto in ["tcp", "udp"]:
                for p in r.dst_ports:
                    if not (1 <= p <= 65535):
                        warnings.append(f"Rule {r.id}: invalid port number {p}.")

            needs_custom_service = False

            if proto in ["tcp", "udp"]:
                if len(r.dst_ports) == 1:
                    port = r.dst_ports[0]
                    if (proto, port) not in WELL_KNOWN_DEFAULT_SERVICES:
                        needs_custom_service = True
                else:
                    needs_custom_service = True

            if needs_custom_service:
                warnings.append(
                    f"Rule {r.id}: No built-in PAN-OS application covers {proto}/{r.dst_ports}. "
                    f"A custom service-object will likely be required."
                )

            if r.direction == "inbound" and r.src_zone.lower() in ["internal", "trust"]:
                warnings.append(
                    f"Rule {r.id}: inbound rule has internal src_zone '{r.src_zone}'."
                )

            if r.direction == "outbound" and r.dst_zone.lower() in ["internal", "trust"]:
                warnings.append(
                    f"Rule {r.id}: outbound rule has internal dst_zone '{r.dst_zone}'."
                )

            if set(r.src) & set(r.dst):
                warnings.append(
                    f"Rule {r.id}: same object(s) appear in both source and destination."
                )

            for obj in r.src + r.dst:
                if _is_ip_or_cidr(obj):
                    continue

                if any(c in INVALID_NAME_CHARS for c in obj):
                    warnings.append(
                        f"Rule {r.id}: object name '{obj}' contains invalid characters for PAN-OS."
                    )

        return (len(warnings) == 0), warnings