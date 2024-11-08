from application.telegram.handlers.user_chats.user_chat_menu.meeting_menu_handlers import MeetingMenuHandlers
from application.meetings.services.meeting_menu_service import MeetingMenuService
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.config.assistants.meeting_assistant_config import meeting_assistant
from infrastructure.config.scheduler.meeting_job_service import meeting_job_service
from infrastructure.config.user_chats.meetings.meeting_notifications_config import telegram_meeting_notifications_service

meeting_menu_service = MeetingMenuService(repositroties_dependency_provider_async, meeting_assistant,
                                          telegram_meeting_notifications_service,
                                          meeting_job_service)

meeting_menu_handlers = MeetingMenuHandlers(meeting_menu_service)

meeting_menu_router = meeting_menu_handlers.get_router()