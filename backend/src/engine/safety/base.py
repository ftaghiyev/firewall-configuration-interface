from abc import ABC, abstractmethod
from typing import Tuple, List
from ..schemas import IRBuilderOutput


class SafetyGate(ABC):

    @abstractmethod
    def enforce(self, ir: IRBuilderOutput) -> Tuple[bool, List[str]]:
        pass