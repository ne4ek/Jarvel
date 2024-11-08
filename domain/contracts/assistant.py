from abc import ABC, abstractmethod
from typing import List, Dict

class Assistant(ABC):
    @abstractmethod
    def __init__(self, api_key: str, model: str, temperature: int, prompt: str):
        pass
    
    @abstractmethod
    def get_all_parameters(self, messages: List[Dict]):
        pass
    
    @abstractmethod
    def compose_telegram_filling_message(self):
        pass 