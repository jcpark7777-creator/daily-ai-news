from abc import ABC, abstractmethod


class AIProvider(ABC):
    @abstractmethod
    def generate_json(self, prompt: str) -> str:
        raise NotImplementedError
