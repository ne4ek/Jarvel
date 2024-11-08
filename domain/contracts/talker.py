from abc import ABC, abstractmethod
from typing import List, Dict


class Talker(ABC):
    @abstractmethod
    def __init__(self, api_key: str, model: str, temperature: str, prompt: str):
        pass
    
    @abstractmethod
    def get_response(self, messages: List[Dict[str, str]]):
        pass