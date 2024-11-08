from application.tasks.services.send_task_notification_service import SendTaskNotificationService
from application.telegram.handlers.user_chats.task_notifications_handlers import TaskNotificationsHandlers
from application.tasks.services.user_chat_tasks_service import UserChatTaskService
from infrastructure.config.bot_config import bot
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async



task_notification_service = SendTaskNotificationService(bot=bot,
                                                        repository_provivder=repositroties_dependency_provider_async)
user_chat_service = UserChatTaskService(repository_provider=repositroties_dependency_provider_async,
                                        task_notification_service=task_notification_service)

tasks_notification_handlers = TaskNotificationsHandlers(task_service=user_chat_service)
tasks_notification_router = tasks_notification_handlers.get_router()
