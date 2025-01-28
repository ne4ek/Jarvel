from infrastructure.repositories_impl.postgres.asynchronous.postgres_companies_repository_async import PostgresCompaniesRepositoryAsync
from infrastructure.repositories_impl.postgres.asynchronous.postgres_users_repository_async import PostgresUsersRepositoryAsync
from infrastructure.repositories_impl.postgres.asynchronous.postgres_task_repository_async import PostgresTasksRepositoryAsync
from infrastructure.repositories_impl.postgres.asynchronous.postgres_user_chats_repository_async import PostgresUserChatsRepositoryAsync
from infrastructure.repositories_impl.postgres.asynchronous.postgres_group_chats_repository_async import \
    PostgresGroupChatsRepositoryAsync
from infrastructure.repositories_impl.postgres.asynchronous.postgres_meetings_repository_async import PostgresMeetingsRepositoryAsync
from infrastructure.repositories_impl.postgres.asynchronous.postgres_messages_repository_async import PostgresMessagesRepositoryAsync
from infrastructure.repositories_impl.postgres.asynchronous.postgres_ctrls_repository_async import PostgresCtrlsRepositoryAsync
from infrastructure.repositories_impl.postgres.asynchronous.postgres_mailing_repository_async import PostgresMailingRepositoryAsync
from infrastructure.repositories_impl.postgres.asynchronous.postgres_arbitrary_user_data_repository_async import PostgresArbitraryUserDataRepositoryAsync
from infrastructure.repositories_impl.postgres.asynchronous.postgres_ups_repository_async import PostgresUpRepositoryAsync
from infrastructure.repositories_impl.postgres.asynchronous.postgres_transcribed_voice_message_text_async import PostgresTranscribedVoiceMessageTextAsync
from infrastructure.repositories_impl.postgres.asynchronous.postgres_tunneling_async import PostgresTunnelingAsync

class RepositoriesDependencyProviderImplAsync:
    def __init__(self,
                 users_repository: PostgresUsersRepositoryAsync,
                 companies_repository: PostgresCompaniesRepositoryAsync,
                 tasks_repository: PostgresTasksRepositoryAsync,
                 meetings_repository: PostgresMeetingsRepositoryAsync,
                 messages_repository: PostgresMessagesRepositoryAsync,
                 user_chats_repository: PostgresUserChatsRepositoryAsync,
                 group_chats_repository: PostgresGroupChatsRepositoryAsync,
                 mailing_repository: PostgresMailingRepositoryAsync,
                 arbitrary_data_repository: PostgresArbitraryUserDataRepositoryAsync,
                 ctrls_repository: PostgresCtrlsRepositoryAsync,
                 ups_repository: PostgresUpRepositoryAsync,
                 transcribed_voice_message_text_repository: PostgresTranscribedVoiceMessageTextAsync,
                 tunneling_repository: PostgresTunnelingAsync,
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
        self.ups_repository = ups_repository
        self.transcribed_voice_message_text_repository = transcribed_voice_message_text_repository
        self.tunneling_repository = tunneling_repository

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
    
    def get_ctrls_repository(self) -> PostgresCtrlsRepositoryAsync:
        return self.ctrls_repository

    def get_ups_repository(self) -> PostgresUpRepositoryAsync:
        return self.ups_repository
    
    def get_transcribed_voice_message_text_repository(self) -> PostgresTranscribedVoiceMessageTextAsync:
        return self.transcribed_voice_message_text_repository
    
    def get_tunneling_repository(self) -> PostgresTunnelingAsync:
        return self.tunneling_repository