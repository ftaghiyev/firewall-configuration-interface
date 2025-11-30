from abc import ABC, abstractmethod
from typing import List, Tuple
from ..schemas import IRBuilderOutput

class IRLinter(ABC):

    @abstractmethod
    def lint(self, ir: IRBuilderOutput) -> Tuple[bool, List[str]]:
        """Return (is_valid, warnings)."""
        pass
