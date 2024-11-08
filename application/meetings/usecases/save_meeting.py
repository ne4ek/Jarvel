from application.repositories.meetings_repository import MeetingsRepository
from application.notification.services.notification_service import NotificationService
from domain.entities.meeting import Meeting


class SaveMeetingUseCase:
    def __init__(self, meetings_repository: MeetingsRepository, notification_service: NotificationService):
        self.meetings_repository = meetings_repository
        self.notification_service = notification_service

    async def execute(self, meeting: Meeting):
        # self.meetings_repository.save(meeting)
        try:
            await self.meetings_repository.save(meeting)
        except Exception as e:
            pass
            # return False
        # /return True

        if meeting.invitation_type == "email":
            pass
            # self.notification_service.send_email_notification()
        elif meeting.invitation_type == "telegram":
            pass