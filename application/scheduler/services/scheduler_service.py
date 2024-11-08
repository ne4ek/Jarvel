from application.providers.repositories_provider import RepositoriesDependencyProvider
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from domain.entities.job import Job
from typing import List
import datetime
import pytz

class SchedulerService:
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler
    
    def add_job(self, job: Job) -> None:
        current_datetime = datetime.datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        job_time = job.run_date
        #if current_datetime > job_time:
        #    return
        
        func = job.func
        args = job.args
        self.scheduler.add_job(func, trigger="date", run_date=job_time, args=args)

