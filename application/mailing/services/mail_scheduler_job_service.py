from typing import List

import pytz
from application.providers.repositories_provider import RepositoriesDependencyProvider
from domain.entities.job import Job
from domain.entities.mail import Mail
from application.scheduler.services.scheduler_service import SchedulerService
from datetime import timedelta, datetime
from infrastructure.interfaces_impl.email_sender_impl import EmailMailSenderImpl
from infrastructure.interfaces_impl.telegram_sender_impl import TelegramMailSenderImpl


class MailingJobService:
    def __init__(self, repositories: RepositoriesDependencyProvider, scheduler_service: SchedulerService, telegram_sender: TelegramMailSenderImpl, email_sender: EmailMailSenderImpl):
        self.mail_repository = repositories.get_mailing_repository()
        self.scheduler = scheduler_service
        self.telegram_sender = telegram_sender
        self.email_sender = email_sender

    def __handle_send_date(self, mail: Mail):
        if mail.send_at is None:
            mail.send_at = datetime.now(pytz.timezone('Europe/Moscow')) + timedelta(minutes=mail.send_delay)
    async def __handle_telegram_mail(self, mail: Mail):
        if mail.send_delay == 0:
            await self.telegram_sender.send_message(mail)
            return None
        else:
            return Job(func=self.telegram_sender.send_message, trigger="date", run_date=mail.send_at, args=[mail])
        
    async def __handle_email_mail(self, mail: Mail):
        if mail.send_delay == 0:
            await self.email_sender.send_email(mail)
            return None
        else:
            return Job(func=self.email_sender.send_email, trigger="date", run_date=mail.send_at, args=[mail])
        
    async def __create_mail_jobs(self, mail: Mail):
        self.__handle_send_date(mail)
        if mail.contact_type == 'telegram':
            job = await self.__handle_telegram_mail(mail)
            return job
        if mail.contact_type == 'email':
            job = await self.__handle_email_mail(mail)
            return job
        return None
    
    async def add_saved_mail_jobs(self, mail: Mail):
        mail_job = await self.__create_mail_jobs(mail)
        print(mail_job)
        if mail_job is not None:
            self.scheduler.add_job(mail_job)
        
    async def add_all_jobs(self):
        all_jobs = await self.__get_all_mail_jobs()
        for job in all_jobs:
            self.scheduler.add_job(job)

    async def __get_all_mail_jobs(self) -> List[Job]:
        mails = await self.mail_repository.get_all()
        job_list = []
        for mail in mails:
            mail_job = Job(func=self.telegram_sender.send_message, trigger="date", run_date=mail.send_at, args=[mail])
            job_list.extend([mail_job])
        return job_list