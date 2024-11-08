from abc import ABC, abstractmethod

from domain.entities.mail import Mail
class MailingValidator(ABC):
    @staticmethod
    @abstractmethod
    def validate_author(mail: Mail):
        pass
    
    @staticmethod
    @abstractmethod
    def validate_recipients(mail: Mail):
        pass
    
    @staticmethod
    @abstractmethod
    def validate_topic(mail: Mail):
        pass
    
    @staticmethod
    @abstractmethod
    def validate_body(mail: Mail):
        pass
    
    @staticmethod
    @abstractmethod
    def validate_delay(mail: Mail):
        pass
    
    @staticmethod
    @abstractmethod
    def validate_contact_type(mail: Mail):
        pass
    
    @staticmethod
    @abstractmethod
    def validate_created_mail(mail: Mail):
        pass