from application.meetings.services.meeting_scheduler_job_service import MeetingJobService
from infrastructure.config.user_chats.meetings.meeting_notifications_config import telegram_meeting_notifications_service
from .scheduler import scheduler_service
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async


meeting_job_service = MeetingJobService(scheduler_service=scheduler_service,
                                        meeting_notification_service=telegram_meeting_notifications_service,
                                        repositories=repositroties_dependency_provider_async)