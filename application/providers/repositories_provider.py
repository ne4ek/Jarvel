from abc import ABC, abstractmethod

from application.repositories.companies_repository import CompaniesRepository
from application.repositories.group_chats_repository import GroupChatsRepository
from application.repositories.user_chats_repository import UserChatsRepository
from application.repositories.meetings_repository import MeetingsRepository
from application.repositories.mailing_repository import MailingRepository
from application.repositories.messages_repository import MessagesRepository
from application.repositories.tasks_repository import TasksRepository
from application.repositories.users_repository import UsersRepository
from application.repositories.ctrls_repository import CtrlsRepository
from application.repositories.up_repository import UpRepository
from application.repositories.arbitrary_user_data_repository import ArbitraryUserDataRepository



class RepositoriesDependencyProvider(ABC):
    @abstractmethod
    def get_users_repository(self) -> UsersRepository:
        pass

    @abstractmethod
    def get_companies_repository(self) -> CompaniesRepository:
        pass

    @abstractmethod
    def get_tasks_repository(self) -> TasksRepository:
        pass

    @abstractmethod
    def get_meetings_repository(self) -> MeetingsRepository:
        pass

    @abstractmethod
    def get_messages_repository(self) -> MessagesRepository:
        pass

    @abstractmethod
    def get_user_chats_repository(self) -> UserChatsRepository:
        pass

    @abstractmethod
    def get_group_chats_repository(self) -> GroupChatsRepository:
        pass

    @abstractmethod
    def get_mailing_repository(self) -> MailingRepository:
        pass
    
    @abstractmethod
    def get_arbitrary_data_repository(self) -> ArbitraryUserDataRepository:
        pass
    
    @abstractmethod
    def get_ctrls_repository(self) -> CtrlsRepository:
        pass

    @abstractmethod
    def get_ups_repository(self) -> UpRepository:
        pass

