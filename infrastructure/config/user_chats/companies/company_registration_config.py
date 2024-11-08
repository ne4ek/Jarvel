from application.telegram.handlers.user_chats.company.company_registration_handlers import CreateCompanyHandler
from application.companies.usecases.save_company import SaveCompanyUseCase
from application.companies.services.create_company_service import CreateCompanyService
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.providers_impl.usecases_provider_impl import UseCaseProviderImpl
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async


save_company_usecase = SaveCompanyUseCase(companies_repository=repositroties_dependency_provider_async.get_companies_repository(),
                                          user_chats_repository=repositroties_dependency_provider_async.get_user_chats_repository())

usecases = UseCaseProviderImpl(save_company_usecase=save_company_usecase)

company_service = CreateCompanyService(usecases=usecases)

handlers = CreateCompanyHandler(companies_service=company_service)

create_company_router = handlers.get_router()