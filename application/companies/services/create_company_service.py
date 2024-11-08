from application.companies.validators.companies_validators import CompaniesValidator
from application.providers.usecases_provider import UseCasesProvider
from application.telegram.auxiliary import generate_code
from const import WORD_LIST
from domain.entities.company import Company


class CreateCompanyService:
    def __init__(self, usecases: UseCasesProvider):
        self.usecases = usecases

    def set_company_name(self, name: str, company: Company):
        company.name = name

    def set_company_description(self, description: str, company: Company):
        company.description = description

    async def set_company_code(self, code: str | None, company: Company):
        if code is None:
            code = await generate_code(WORD_LIST)
        company.code = code

    def set_company_owner_id(self, owner_id: int, company: Company):
        company.owner_id = owner_id

    def create_company(self) -> Company:
        company = Company(users_id=[])
        return company

    async def save(self, company: Company):
        await self.usecases.save_company_usecase.execute(company)