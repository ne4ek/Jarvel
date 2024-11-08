from application.repositories.companies_repository import CompaniesRepository
from application.repositories.group_chats_repository import GroupChatsRepository
from application.repositories.user_chats_repository import UserChatsRepository
from application.repositories.meetings_repository import MeetingsRepository
from application.repositories.mailing_repository import MailingRepository
from application.providers.repositories_provider import RepositoriesDependencyProvider
from application.repositories.messages_repository import MessagesRepository
from application.repositories.tasks_repository import TasksRepository
from application.repositories.users_repository import UsersRepository
from application.repositories.arbitrary_user_data_repository import ArbitraryUserDataRepository
from infrastructure.config.postgres_config import connection_pool
from infrastructure.repositories_impl.postgres.postgres_companies_repository import PostgresCompaniesRepository
from infrastructure.repositories_impl.postgres.postgres_users_repository import PostgresUsersRepository
from infrastructure.repositories_impl.postgres.postgres_task_repository import PostgresTasksRepository
from infrastructure.repositories_impl.postgres.postgres_user_chats_repository import PostgresUserChatsRepository
from infrastructure.repositories_impl.postgres.postgres_group_chats_repository import \
    PostgresGroupChatsRepository
from infrastructure.repositories_impl.postgres.postgres_meetings_repository import PostgresMeetingsRepository
from infrastructure.repositories_impl.postgres.postgres_messages_repository import PostgresMessagesRepository
from infrastructure.repositories_impl.postgres.postgres_ctrls_repository import PostgresCtrlsRepository


class RepositoriesDependencyProviderImpl(RepositoriesDependencyProvider):
    def __init__(self,
                 users_repository: UsersRepository,
                 companies_repository: CompaniesRepository,
                 tasks_repository: TasksRepository,
                 meetings_repository: MeetingsRepository,
                 messages_repository: MessagesRepository,
                 user_chats_repository: UserChatsRepository,
                 group_chats_repository: GroupChatsRepository,
                 mailing_repository: MailingRepository,
                 arbitrary_data_repository: ArbitraryUserDataRepository,
                 ctrls_repository: PostgresCtrlsRepository
                 ):
        self.users_repository = users_repository
        self.companies_repository = companies_repository
        self.tasks_repository = tasks_repository
        self.meetings_repository = meetings_repository
        self.messages_repository = messages_repository
        self.user_chats_repository = user_chats_repository
        self.group_chats_repository = group_chats_repository
        self.mailing_repository = mailing_repository
        self.arbitrary_data_repository = arbitrary_data_repository
        self.ctrls_repository = ctrls_repository

    def get_users_repository(self):
        return self.users_repository

    def get_companies_repository(self):
        return self.companies_repository

    def get_tasks_repository(self):
        return self.tasks_repository

    def get_meetings_repository(self):
        return self.meetings_repository

    def get_messages_repository(self):
        return self.messages_repository

    def get_user_chats_repository(self):
        return self.user_chats_repository

    def get_group_chats_repository(self):
        return self.group_chats_repository

    def get_mailing_repository(self):
        return self.mailing_repository

    def get_arbitrary_data_repository(self):
        return self.arbitrary_data_repository
    
    def get_ctrls_repository(self):
        return self.ctrls_repository