from application.meetings.services.telegram_meeting_notification_service import SendTelegramMeetingNotificationService
from application.meetings.services.mail_meeting_notification_service import SendEmailMeetingNotificationService
from application.meetings.services.user_chat_meeting_service import UserChatMeetingService
from application.telegram.handlers.user_chats.meeting_notification_handlers import MeetingNotificationsHandlers
from infrastructure.config.bot_config import bot
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async

telegram_meeting_notifications_service = SendTelegramMeetingNotificationService(bot, repositroties_dependency_provider_async)
email_meeting_notification_service = SendEmailMeetingNotificationService(repositories=repositroties_dependency_provider_async,
                                                                         bot=bot)
user_chat_meeting_service = UserChatMeetingService(repositroties_dependency_provider_async, telegram_meeting_notifications_service)
meeting_notifications_handlers = MeetingNotificationsHandlers(notification_meeting_service=user_chat_meeting_service)

meeting_notifications_router = meeting_notifications_handlers.get_router()