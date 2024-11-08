from application.telegram.handlers.user_chats.user_chat_menu.task_menu_handlers import TaskMenuHandlers
from application.telegram.handlers.user_chats.user_chat_menu.task_change_data_handlers import UserChatEditTaskHandlers
from application.tasks.services.user_chat_task_menu_service import TaskMenuService
from application.tasks.services.edit_task_data_service import EditTaskDataService
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.config.assistants.task_assistant_config import task_assistant
from .tasks_notifications_config import task_notification_service

task_menu_service = TaskMenuService(repository_provider=repositroties_dependency_provider_async)
edit_task_data_service = EditTaskDataService(repositories_provider=repositroties_dependency_provider_async,
                                             task_assistant=task_assistant,
                                             task_notification_service=task_notification_service)

task_menu_handlers = TaskMenuHandlers(task_menu_service=task_menu_service)
task_change_data_handlers = UserChatEditTaskHandlers(edit_task_data_service,
                                                     task_menu_service)

task_menu_router = task_menu_handlers.get_router()
task_change_data_router = task_change_data_handlers.get_router()