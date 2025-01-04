from application.providers.repositories_provider import RepositoriesDependencyProvider
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from domain.entities.job import Job
from typing import List
import datetime
import pytz
from icecream import ic

class SchedulerService:
    def __init__(self, scheduler: AsyncIOScheduler):
        self.scheduler = scheduler
    
    def add_job(self, job: Job) -> None:
        job_time = job.run_date
        
        job_id = str(job.job_id)
        ic(job_id)
        func = job.func
        args = job.args
        if job_id and job_id != "None":
            self.scheduler.add_job(func, trigger="date", run_date=job_time, id=job_id, args=args)
        else:
            self.scheduler.add_job(func, trigger="date", run_date=job_time, args=args)
        
    def remove_job(self, job_id: str):
        self.scheduler.remove_job(job_id)

