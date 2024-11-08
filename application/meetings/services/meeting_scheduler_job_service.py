from application.providers.repositories_provider import RepositoriesDependencyProvider
from application.scheduler.services.scheduler_service import SchedulerService
from domain.entities.job import Job
from domain.entities.meeting import Meeting
from .telegram_meeting_notification_service import SendTelegramMeetingNotificationService
from typing import List
from datetime import datetime, timedelta
import pytz

class MeetingJobService:
    def __init__(self, repositories: RepositoriesDependencyProvider, scheduler_service: SchedulerService, meeting_notification_service: SendTelegramMeetingNotificationService):
        self.meeting_repository = repositories.get_meetings_repository()
        self.scheduler = scheduler_service
        self.meeting_notification_service = meeting_notification_service
    
    def add_meeting_job(self, job: Job):
        self.scheduler.add_job(job)
    
    def add_saved_meetings_jobs(self, meeting: Meeting):
        meeting_remind_datetime = meeting.remind_datetime
        
        remind_participants_job = Job(func=self.meeting_notification_service.send_meeting_reminder_to_participants,
                                      args=[meeting.meeting_id, meeting.remind_datetime], run_date=meeting_remind_datetime)
        remind_moderator_job = Job(func=self.meeting_notification_service.send_meeting_reminder_to_moderator,
                                   args=[meeting.meeting_id, meeting.remind_datetime], run_date=meeting_remind_datetime)
        set_status_job = Job(func=self.change_meeting_status, args=[meeting, "complete"],
                             run_date=meeting.meeting_datetime + timedelta(minutes=int(meeting.duration)))
        self.scheduler.add_job(remind_participants_job)
        self.scheduler.add_job(remind_moderator_job)
        self.scheduler.add_job(set_status_job)
    
    async def add_all_jobs(self):
        all_jobs = await self.__get_all_meeting_jobs()
        for job in all_jobs:
            self.scheduler.add_job(job)
    
    async def change_meeting_status(self, meeting: Meeting, status: str):
        if meeting.status == "pending" and status in ["complete", "cancelled"]:
            await self.meeting_repository.set_status(meeting_id=meeting.meeting_id, status=status)
    
    async def __get_all_meeting_jobs(self) -> List[Job]:
        meetings = await self.meeting_repository.get_all()
        job_list = []
        for meeting in meetings:
            if meeting.meeting_datetime < datetime.now(tz=meeting.meeting_datetime.tzinfo) or meeting.status in ["complete", "cancelled"]:
                continue
            remind_moderator_job = Job(func=self.meeting_notification_service.send_meeting_reminder_to_moderator, args=[meeting.meeting_id, meeting.remind_datetime], run_date=meeting.remind_datetime)
            remind_participants_job = Job(func=self.meeting_notification_service.send_meeting_reminder_to_participants, args=[meeting.meeting_id, meeting.remind_datetime], run_date=meeting.remind_datetime)
            set_status_job = Job(func=self.change_meeting_status, args=[meeting, "complete"],
                                 run_date=meeting.meeting_datetime + timedelta(minutes=int(meeting.duration)))
            job_list.extend([remind_moderator_job, remind_participants_job, set_status_job])
        return job_list