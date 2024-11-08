from abc import ABC, abstractmethod
from typing import Union, Dict

class ArbitraryUserDataRepository(ABC):
    @abstractmethod
    def get_arbitrary_user_data(self, user_id: int) -> str:
        pass
    
    @abstractmethod
    def set_arbitrary_user_data(self, user_id: int, arbitrary_data: str):
        pass