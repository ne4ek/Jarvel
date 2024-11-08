from application.email.interfaces.send_email_interface import EmailSenderInterface
from application.notification.services.notification_service import NotificationService
from application.telegram.interfaces.telegram_sender_interface import TelegramSenderInterface
from domain.entities.message import Message
from domain.entities.mail import Mail

class SendMailUseCase:
    def __init__(self,
                 telegram_sender_interface: TelegramSenderInterface,
                 email_sender_interface: EmailSenderInterface
                 ):
        self.telegram_sender_interface = telegram_sender_interface
        self.email_sender_interface = email_sender_interface

    def execute(self, mail: Mail):
        if mail.contact_type == 'telegram':
            self.telegram_sender_interface.send_message(mail=mail)
        elif mail.contact_type == 'email':
            self.email_sender_interface.send_email(mail=mail)