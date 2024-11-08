from application.providers.repositories_provider import RepositoriesDependencyProvider
from domain.entities.task import Task
from domain.entities.job import Job
from application.scheduler.services.scheduler_service import SchedulerService
from .send_task_notification_service import SendTaskNotificationService
from datetime import timedelta, datetime
from typing import List

class TaskJobService:
    def __init__(self, repositories: RepositoriesDependencyProvider, task_notification_service: SendTaskNotificationService, scheduler_service: SchedulerService):
        self.task_repository = repositories.get_tasks_repository()
        self.task_notification_service = task_notification_service
        self.scheduler = scheduler_service
    
    def add_task_job(self, job: Job):
        self.scheduler.add_job(job)
        
    
    def add_saved_task_jobs(self, task: Task):
        reminder_job = Job(func=self.task_notification_service.send_task_reminder, trigger="date", run_date=task.deadline_datetime - timedelta(minutes=1), args=[task])
        overdue_job = Job(func=self.task_notification_service.send_task_is_overdue, trigger="date", run_date=task.deadline_datetime + timedelta(minutes=1), args=[task])
        self.scheduler.add_job(reminder_job)
        self.scheduler.add_job(overdue_job)
    
    async def add_all_jobs(self):
        all_jobs = await self.__get_all_tasks_jobs()
        for job in all_jobs:
            self.scheduler.add_job(job)
    
    async def __get_all_tasks_jobs(self) -> List[Job]:
        tasks = await self.task_repository.get_all()
        job_list = []
        for task in tasks:
            if task.status in ("complete", "overdue", "cancelled") or task.deadline_datetime < datetime.now(tz=task.deadline_datetime.tzinfo):
                continue
            reminder_job = Job(func=self.task_notification_service.send_task_reminder, trigger="date", run_date=task.deadline_datetime - timedelta(minutes=2), args=[task])
            if task.status not in ("complete", "cancelled", "overdue"):
                overdue_job = Job(func=self.task_notification_service.send_task_is_overdue, trigger="date", run_date=task.deadline_datetime + timedelta(minutes=1), args=[task])
            job_list.extend([reminder_job, overdue_job])
        return job_list