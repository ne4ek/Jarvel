# src/application/usecases/schedule_jobs.py
from datetime import datetime, timedelta

from application.repositories.meetings_repository import MeetingsRepository
from application.repositories.notifications_repository import NotificationsRepository
from application.repositories.mailing_repository import MailingRepository
from application.scheduler.interfaces.scheduler_interface import SchedulerInterface
from domain.entities.job import Job
from domain.entities.message import Message


# from application.services.scheduler_service import SchedulerService
# from application.repositories.meeting_repository import MeetingRepository
# from application.repositories.scheduler_repository import SchedulerRepository


class SetAllSchedulersJobsUseCase:
    def __init__(self,
                 scheduler_interface: SchedulerInterface,
                 meetings_repository: MeetingsRepository,
                 notifications_repository: NotificationsRepository,
                 mailing_repository: MailingRepository
                 ):

        self.scheduler_interface = scheduler_interface
        self.meetings_repository = meetings_repository
        self.notifications_repository = notifications_repository
        self.mailing_repository = mailing_repository

    def execute(self):
        #self.set_meetings()
        pass

    async def set_meetings(self):
        meetings = await self.meetings_repository.get_all()
        for meeting in meetings:
            func = None
            if meeting.invitation_type == 'telegram':
                func = self.set_send_meeting_message_telegram
            elif meeting.invitation_type == 'email':
                func = self.set_send_meeting_message_email
            if func:
                self.scheduler_interface.add_job(Job(
                    func=func,
                    trigger='date',
                    run_date=meeting.meeting_datetime - timedelta(minutes=5),
                    args=[meeting]
                ))
                self.scheduler_interface.add_job(Job(
                    func=self.set_send_meeting_message_telegram,
                    trigger='date',
                    run_date=meeting.remind_datetime,
                    args=[meeting]
                ))

    def set_send_meeting_message_telegram(self, meeting):
        pass
        # message = Message(
        #     text=f"Reminder: Meeting '{meeting.topic}' is starting soon.",
        #     recipient=meeting.moderator_id  # Assuming moderator_id is the telegram ID
        # )
        # self.notification_service.send_telegram_notification(message)

    def set_send_meeting_message_email(self, meeting):
        # Implementation for sending email notification
        pass
