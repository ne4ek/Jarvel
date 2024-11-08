from abc import ABC, abstractmethod
from domain.entities.email import Email
from domain.entities.mail import Mail


class EmailSenderInterface(ABC):
    @abstractmethod
    def send_email(self, mail: Mail):
        pass

    @abstractmethod
    def send_email_sync(self, mail: Mail):
        pass
