from application.companies.validators.companies_validators import CompaniesValidator
from application.providers.usecases_provider import UseCasesProvider

from application.providers.repositories_provider import RepositoriesDependencyProvider
from domain.entities.user_chat import UserChat


class JoinCompanyService:
    def __init__(self, companies_validator: CompaniesValidator,
                 repository_dependency_provider: RepositoriesDependencyProvider,
                 usecases: UseCasesProvider):
        self.companies_repository = repository_dependency_provider.get_companies_repository()
        self.user_repository = repository_dependency_provider.get_users_repository()
        self.companies_validator = companies_validator
        self.usecases = usecases

    async def set_company_code(self, code: str, user_chat: UserChat):
        try:
            await self.companies_validator.validate_code(self.companies_repository, code)
            user_chat.company_code = code
        except Exception as e:
            raise e

    async def is_user_registered_in_company(self, code: str, user_id: int):
        return await self.companies_repository.is_user_registered_in_company(code, user_id)

    def set_role(self, role: str, user_chat: UserChat):
        user_chat.role = role
        
    async def is_user_registered(self, user_chat: UserChat):
        await self.user_repository.is_user_exists(user_chat.user_id)

    async def save_user(self, user_chat: UserChat):
        await self.__add_user_in_company(user_chat)
        
    async def __add_user_in_company(self, user_chat: UserChat):
        await self.companies_repository.add_user_id_by_company_code(user_id=user_chat.user_id, company_code=user_chat.company_code, role=user_chat.role)
        
    def create_user_chat(self, user_id):
        return UserChat(
            user_id=user_id,
            role=None,
            company_code=None
        )