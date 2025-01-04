from abc import ABC, abstractmethod
from domain.entities.up_message import UpMessage
from datetime import datetime, timedelta
from typing import Union, Dict, List

class UpRepository(ABC):
    @abstractmethod
    def __init__(self, connection) -> None:
        pass
    
    @abstractmethod
    def save(self, up_message: UpMessage) -> None:
        pass
    
    @abstractmethod
    def get_all(self, up_message: UpMessage) -> List[UpMessage]:
        pass
    
    @abstractmethod
    def update_time(self, up_message: UpMessage, new_interval: timedelta, 
                                               new_next_up_date: datetime) -> None:
        pass
    
    @abstractmethod
    def get_by_up_id(self, up_id: int) -> UpMessage:
        pass