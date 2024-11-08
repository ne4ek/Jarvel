from application.companies.validators.companies_validators import CompaniesValidator
from application.repositories.companies_repository import CompaniesRepository
from domain.custom_errors.company_errors.invalid_company_length import InvalidCompanyLength
from domain.custom_errors.company_errors.company_code_not_found import CompanyCodeNotFound
from domain.entities.company import Company


class CompaniesValidatorImpl(CompaniesValidator):
    @staticmethod
    def validate_name(name: str, company: Company = None):
        if name is None:
            raise ValueError

    @staticmethod
    async def validate_code(companies_repository: CompaniesRepository, code: str, company: Company = None):
        if len(code.split(' ')) != 1:
            raise InvalidCompanyLength
        is_company_code_exsits = await companies_repository.is_company_code_exists(code)
        if not is_company_code_exsits:
            raise CompanyCodeNotFound

    @staticmethod
    def validate_role(role: str, company: Company = None):
        if role is None:
            raise ValueError

    @staticmethod
    def validate_description(description: str, company: Company = None):
        if description is None:
            raise ValueError

    @staticmethod
    def validate_owner_id(owner_id: int, company: Company = None):
        if owner_id is None:
            raise ValueError

    @staticmethod
    def validate_users_id(users_id: list[int], company: Company = None):
        if users_id is None:
            raise ValueError

