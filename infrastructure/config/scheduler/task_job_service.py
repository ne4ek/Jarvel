from infrastructure.config.user_chats.tasks.tasks_notifications_config import task_notification_service
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from application.tasks.services.task_scheduler_job_service import TaskJobService
from .scheduler import scheduler_service

task_job_service = TaskJobService(scheduler_service=scheduler_service,
                                  task_notification_service=task_notification_service,
                                  repositories=repositroties_dependency_provider_async)