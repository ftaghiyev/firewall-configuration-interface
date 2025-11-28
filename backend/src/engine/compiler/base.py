from abc import ABC, abstractmethod
from typing import Any, Dict

class VendorCompiler(ABC):
    @abstractmethod
    def compile_rule(self, ir_rule: Dict[str, Any]) -> str:
        """
        Compile an intermediate representation (IR) rule into a vendor-specific configuration command.

        Args:
            ir_rule (Dict[str, Any]): The intermediate representation of the firewall rule.
        Returns:
            str: The vendor-specific configuration command.
        """

        pass

    @abstractmethod
    def compile_policy(self, ir_policy: Dict[str, Any]) -> str:
        """
        Compile an entire intermediate representation (IR) policy into vendor-specific configuration commands.

        Args:
            ir_policy (Dict[str, Any]): The intermediate representation of the entire firewall policy.
        Returns:
            str: The vendor-specific configuration commands for the entire policy.
        """

        pass