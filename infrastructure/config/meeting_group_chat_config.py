from application.telegram.handlers.group_chats.meetings.compose_meeting_handlers import ComposeMeetingHandlers
from application.meetings.services.telegram_compose_meeting_service import TelegramComposeMeetingService
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.config.assistants.meeting_assistant_config import meeting_assistant
from infrastructure.config.user_chats.meetings.meeting_notifications_config import telegram_meeting_notifications_service, email_meeting_notification_service
from infrastructure.config.scheduler.meeting_job_service import meeting_job_service


telegram_meeting_service = TelegramComposeMeetingService(repositroties_dependency_provider_async, 
                                                         telegram_meeting_notifications_service,
                                                         email_meeting_notification_service,
                                                         meeting_assistant,
                                                         meeting_job_service)

meeting_handlers = ComposeMeetingHandlers(telegram_meeting_service)

meeting_router = meeting_handlers.get_router()