from application.repositories.companies_repository import CompaniesRepository
from application.repositories.user_chats_repository import UserChatsRepository
from domain.entities.company import Company
from domain.entities.user_chat import UserChat


class SaveCompanyUseCase:
    def __init__(self, companies_repository: CompaniesRepository, user_chats_repository: UserChatsRepository):
        self.companies_repository = companies_repository
        self.user_chats_repository = user_chats_repository

    async def execute(self, company: Company):
        await self.companies_repository.save(company)
