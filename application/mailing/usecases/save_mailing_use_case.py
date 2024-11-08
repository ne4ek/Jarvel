from application.email.interfaces.send_email_interface import EmailSenderInterface
from application.repositories.mailing_repository import MailingRepository
from application.scheduler.interfaces.scheduler_interface import SchedulerInterface
from application.telegram.interfaces.telegram_sender_interface import TelegramSenderInterface
from domain.entities.job import Job
from domain.entities.mail import Mail
from datetime import datetime
import pytz

class SaveMailingUseCase:
    def __init__(self,
                 mailing_repository: MailingRepository,
                 scheduler_interface: SchedulerInterface,
                 telegram_sender_interface: TelegramSenderInterface,
                 email_sender_interface: EmailSenderInterface
                 ):
        self.mailing_repository = mailing_repository
        self.scheduler_interface = scheduler_interface
        self.telegram_sender_interface = telegram_sender_interface
        self.email_sender_interface = email_sender_interface


    async def execute(self, mailing: Mail):
        await self.mailing_repository.save(mailing)
        self.set_job(mailing)
        # Отправить
        pass

    def set_job(self, mailing: Mail):
        if mailing.send_at is None:
            current_datetime = datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
            mailing.send_datetime = current_datetime + mailing.send_delay

        func = None
        if mailing.contact_type == 'telegram':
           func = self.telegram_sender_interface.send_message

        elif mailing.contact_type == 'email':
            func = self.email_sender_interface.send_email

        self.scheduler_interface.add_job(
            Job(
                func=func,
                trigger="date",
                run_date=mailing.send_datetime,
                args=[mailing]
            )
        )