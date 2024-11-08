from application.providers.repositories_provider import RepositoriesDependencyProvider
from application.scheduler.interfaces.scheduler_interface import SchedulerInterface
from application.scheduler.usecases.set_all_scheduler_use_case import SetAllSchedulersJobsUseCase


class SetAllSchedulersService:
    def __init__(self, scheduler_interface: SchedulerInterface, repositroties_dependency_provider_async: RepositoriesDependencyProvider):
        self.scheduler_interface = scheduler_interface
        self.repositroties_dependency_provider_async = repositroties_dependency_provider_async

        self.scheduler_use_case = SetAllSchedulersJobsUseCase(
            scheduler_interface=scheduler_interface,
            meetings_repository=self.get_meetings_repository,
            notifications_repository=self.get_notifications_repository,
            mailing_repository=self.get_mailing_repository
        )

    @property
    def get_meetings_repository(self):
        return self.repositroties_dependency_provider_async.get_meetings_repository()

    @property
    def get_notifications_repository(self):
        return self.repositroties_dependency_provider_async.get_notifications_repository()
    @property
    def get_mailing_repository(self):
        return self.repositroties_dependency_provider_async.get_mailing_repository()

    def execute(self):
        self.scheduler_use_case.execute()

