
from application.mailing.services.user_chat_compose_mailing_service import UserChatComposeMailService
from application.telegram.handlers.user_chats.user_chat_menu.user_chat_compose_mailing_handlers import UserChatsComposeMailHandlers
from infrastructure.config.assistants.mailing_assistant_config import mailing_assistant
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.config.scheduler.mailing_job_service import mail_job_service

mailing_job_service = mail_job_service
telegram_mail_service = UserChatComposeMailService(repository_provider = repositroties_dependency_provider_async,
                                                   mailing_assistant = mailing_assistant,
                                                   mail_job_service = mailing_job_service)
compose_mail_handlers = UserChatsComposeMailHandlers(telegram_mail_service)
user_compose_mail_router = compose_mail_handlers.get_router()
