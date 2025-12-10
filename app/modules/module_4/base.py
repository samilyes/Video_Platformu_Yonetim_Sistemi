# app/modules/module_4/base.py
from abc import ABC, abstractmethod

class BaseClass4(ABC):
    def __init__(self, parameter: str):
        self.base4Attribute = parameter

    @abstractmethod
    def method4(self) -> None:
        """metod tanimi."""
        pass