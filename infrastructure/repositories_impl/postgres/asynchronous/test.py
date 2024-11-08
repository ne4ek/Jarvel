from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.config.dependency_provider_config import repositroties_dependency_provider
from infrastructure.config.postgres_config_async import loop

# сравнение данных, которые возвращают репозитории

company_repo_async = repositroties_dependency_provider_async.get_companies_repository()
company_repo_sync = repositroties_dependency_provider.get_companies_repository()


# loop.run_until_complete(company_repo_async.get_company_code_by_chat_id(1))
# company_repo_sync.get_company_code_by_chat_id(-1002108186059)

# loop.run_until_complete(company_repo_async.get_owner_id_by_company_code("COMPA"))
# company_repo_sync.get_owner_id_by_company_code("SoulCalm")

# loop.run_until_complete(company_repo_async.is_company_code_exists("COMPA"))
# company_repo_sync.is_company_code_exists('BlissSymphony')

ctrls_repo_async = repositroties_dependency_provider_async.get_ctrls_repository()
ctrl_repo_sync = repositroties_dependency_provider.get_ctrls_repository()

ctrl_repo_sync.get_all()
loop.run_until_complete(ctrls_repo_async.get_all())