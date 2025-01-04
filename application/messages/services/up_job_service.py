from infrastructure.providers_impl.repositories_provider_async_impl import RepositoriesDependencyProviderImplAsync
from application.scheduler.services.scheduler_service import SchedulerService
from application.messages.usecases.send_up_message_usecase import SendUpUseCase
from domain.entities.job import Job
from domain.entities.up_message import UpMessage
from typing import List
from icecream import ic


class UpJobService:
    def __init__(self, repositories: RepositoriesDependencyProviderImplAsync, scheduler_service: SchedulerService, send_up_usecase: SendUpUseCase):
        self.ups_repository = repositories.get_ups_repository()
        self.scheduler_service = scheduler_service
        self.send_up_usecase = send_up_usecase
        
    def add_up_job(self, job: Job):
        self.scheduler_service.add_job(job)
    
    def add_saved_up_job(self, up: UpMessage):
        job = Job(func=self.send_up_usecase.execute, trigger="date", run_date=up.next_up_date, job_id=up.up_message_id, args=[up], )
        self.scheduler_service.add_job(job)
    
    async def add_all_jobs(self):
        all_up_jobs = await self.__get_all_up_jobs() 
        for job in all_up_jobs:
            self.scheduler_service.add_job(job)
    
    async def __get_all_up_jobs(self) -> List[Job]:
        ups = await self.ups_repository.get_all()
        job_list = []
        for up in ups:
            if up.is_active:
                job_list.append(Job(func=self.send_up_usecase.execute, trigger="date", run_date=up.next_up_date, job_id=up.up_message_id, args=[up]))
        return job_list
    
    def remove_job_by_id(self, job_id: int):
        self.scheduler_service.remove_job(str(job_id))