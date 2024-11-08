from abc import ABC, abstractmethod
from datetime import datetime

from domain.entities.message import Message
from domain.entities.mail import Mail


class NotificationsRepository(ABC):

    @abstractmethod
    def save(self, notification: Mail):
        pass