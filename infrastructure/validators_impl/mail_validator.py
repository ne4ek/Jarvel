from application.mailing.validators.mailing_validators import MailingValidator
from domain.entities.mail import Mail


class MailingValidatorImpl(MailingValidator):
    @staticmethod
    def validate_author(mail: Mail):
        if mail.author_user is None:
            raise ValueError
    
    @staticmethod
    def validate_recipients(mail: Mail):
        if mail.recipients is None:
            raise ValueError
    
    @staticmethod
    def validate_topic(mail: Mail):
        if mail.topic is None:
            raise ValueError
    
    @staticmethod
    def validate_body(mail: Mail):
        if mail.body is None:
            raise ValueError
    
    @staticmethod
    def validate_delay(mail: Mail):
        if mail.send_delay is None:
            raise ValueError
    
    @staticmethod
    def validate_contact_type(mail: Mail):
        if mail.contact_type is None:
            raise ValueError
    
    @staticmethod
    def validate_created_mail(mail: Mail):
        try:
            MailingValidatorImpl.validate_author(mail)
            MailingValidatorImpl.validate_body(mail)
            MailingValidatorImpl.validate_topic(mail)
            MailingValidatorImpl.validate_contact_type(mail)
            MailingValidatorImpl.validate_recipients(mail)
            MailingValidatorImpl.validate_delay(mail)
            return True
        except:
            return False