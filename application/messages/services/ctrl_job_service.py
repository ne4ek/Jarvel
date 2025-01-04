from application.providers.repositories_provider import RepositoriesDependencyProvider
from application.scheduler.services.scheduler_service import SchedulerService
from application.messages.usecases.send_ctrl_message_usecase import SendCtrlUseCase
from domain.entities.job import Job
from domain.entities.ctrl_message import CtrlMessage
from typing import List
from icecream import ic

class CtrlJobService:
    def __init__(self, repositories: RepositoriesDependencyProvider, scheduler_service: SchedulerService, send_ctrl_usecase: SendCtrlUseCase):
        self.ctrls_repository = repositories.get_ctrls_repository()
        self.scheduler_service = scheduler_service
        self.send_ctrl_usecase = send_ctrl_usecase
    
    def add_ctrl_job(self, job: Job):
        self.scheduler_service.add_job(job)
    
    def add_saved_ctrl_job(self, ctrl: CtrlMessage):
        job = Job(func=self.send_ctrl_usecase.execute, trigger="date", run_date=ctrl.run_date, args=[ctrl])
        self.scheduler_service.add_job(job)
    
    async def add_all_jobs(self):
        all_ctrl_jobs = await self.__get_all_ctrl_jobs() 
        for job in all_ctrl_jobs:
            self.scheduler_service.add_job(job)
    
    async def __get_all_ctrl_jobs(self) -> List[Job]:
        ctrls = await self.ctrls_repository.get_all()
        job_list = []
        for ctrl in ctrls:
            job_list.append(Job(func=self.send_ctrl_usecase.execute, trigger="date", run_date=ctrl.run_date, args=[ctrl]))
        return job_list