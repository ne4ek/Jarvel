from abc import ABC, abstractmethod
from datetime import datetime
from domain.entities.mail import Mail
from typing import List

class MailingRepository(ABC):
    """
    Mailing repository abstract class.
    """

    @abstractmethod
    def get_by_id(self, mailing_id: int) -> Mail:
        pass

    @abstractmethod
    def save(self, mailing: Mail) -> None:
        pass

    @abstractmethod
    def get_all(self) -> list[Mail]:
        pass

    @abstractmethod
    def get_by_author(self, user_id: int):
        pass

    @abstractmethod
    def get_by_mailing_id(self, meeting_id: int) -> Mail:
        pass

    @abstractmethod
    def delete(self, mailing_id) -> None:
        pass