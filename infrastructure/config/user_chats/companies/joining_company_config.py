from application.telegram.handlers.user_chats.company.joining_company_handlers import JoinCompanyHandlers
from application.companies.services.join_company_service import JoinCompanyService
from infrastructure.validators_impl.companies_validator import CompaniesValidatorImpl
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.providers_impl.usecases_provider_impl import UseCaseProviderImpl


usecases = UseCaseProviderImpl()

company_validator = CompaniesValidatorImpl()
companies_validator = CompaniesValidatorImpl()

company_service = JoinCompanyService(companies_validator=company_validator,
                                     repository_dependency_provider=repositroties_dependency_provider_async,
                                     usecases=usecases)

handlers = JoinCompanyHandlers(companies_service=company_service)

join_company_router = handlers.get_router()