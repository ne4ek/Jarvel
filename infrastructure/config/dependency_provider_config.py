from infrastructure.config.postgres_repositories_config import users_rep, companies_rep, tasks_rep, meetings_rep, \
    messages_rep, user_chats_rep, group_chats_rep, mailing_rep, arbitrary_rep, ctrls_rep
from infrastructure.providers_impl.repositories_provider_impl import RepositoriesDependencyProviderImpl

repositories_dependency_provider = RepositoriesDependencyProviderImpl(
    users_repository=users_rep,
    companies_repository=companies_rep,
    tasks_repository=tasks_rep,
    meetings_repository=meetings_rep,
    messages_repository=messages_rep,
    user_chats_repository=user_chats_rep,
    group_chats_repository=group_chats_rep,
    mailing_repository=mailing_rep,
    arbitrary_data_repository=arbitrary_rep,
    ctrls_repository=ctrls_rep
)
