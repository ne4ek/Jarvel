from application.telegram.handlers.group_chats.mailing.compose_mailing_handlers import ComposeMailHandlers
from application.mailing.services.telegram_compose_mailing_service import TelegramComposeMailService
from infrastructure.config.assistants.mailing_assistant_config import mailing_assistant
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.config.scheduler.mailing_job_service import mail_job_service

mailing_job_service = mail_job_service
telegram_mail_service = TelegramComposeMailService(repository_provider = repositroties_dependency_provider_async,
                                                   mailing_assistant = mailing_assistant,
                                                   mail_job_service = mailing_job_service)
compose_mail_handlers = ComposeMailHandlers(telegram_mail_service)
compose_mail_router = compose_mail_handlers.get_router()
