from abc import ABC, abstractmethod
from typing import Any


class BaseGraph(ABC):
    @abstractmethod
    def __init__(self, llm):
        pass

    @abstractmethod
    def chat(self, *args, **kwargs) -> Any:
        pass