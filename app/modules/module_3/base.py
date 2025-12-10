# app/modules/module_3/base.py
from abc import ABC, abstractmethod

class BaseClass3(ABC):
    def __init__(self, parameter: str):
        self.base3Attribute = parameter

    @abstractmethod
    def method3(self) -> None:
        """metod tanimi."""
        pass