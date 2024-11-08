from abc import ABC, abstractmethod


class FunctionCallsProvider(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def add_function_calls(self, function_call: dict):
        pass

    @abstractmethod
    def get_function_call(self, function_name: str) -> dict:
        pass