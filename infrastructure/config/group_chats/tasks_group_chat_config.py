from application.telegram.handlers.group_chats.tasks.compose_task_handlers import ComposeTaskHandlers
from application.tasks.services.telegram_compose_task_service import TelegramComposeTaskService
from infrastructure.providers_impl.usecases_provider_impl import UseCaseProviderImpl
from infrastructure.config.assistants.task_assistant_config import task_assistant
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.config.user_chats.tasks.tasks_notifications_config import task_notification_service
from infrastructure.config.scheduler.task_job_service import task_job_service


usecases = UseCaseProviderImpl()

telegram_compose_task_service = TelegramComposeTaskService(repository_provider=repositroties_dependency_provider_async,
                                                            task_assistant=task_assistant,
                                                            task_notification_sender=task_notification_service,
                                                            task_job_service=task_job_service)

task_handlers = ComposeTaskHandlers(telegram_compose_task_service)

task_router = task_handlers.get_router()