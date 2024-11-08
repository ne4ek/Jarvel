from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from application.mailing.services.mail_scheduler_job_service import MailingJobService
from infrastructure.config.interfaces_config import telegram_sender_interface, email_sender_interface
from .scheduler import scheduler_service

mail_job_service = MailingJobService(scheduler_service=scheduler_service, repositories=repositroties_dependency_provider_async,
                                     telegram_sender=telegram_sender_interface, email_sender=email_sender_interface)