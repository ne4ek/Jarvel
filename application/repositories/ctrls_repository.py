from abc import ABC, abstractmethod

from domain.entities.ctrl_message import CtrlMessage


class CtrlsRepository(ABC):
    @abstractmethod
    def save(ctrl_message: CtrlMessage):
        pass
    
    @abstractmethod
    def get_all():
        pass