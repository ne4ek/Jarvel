from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.providers_impl.usecases_provider_impl import UseCaseProviderImpl
from application.telegram.handlers.user_chats.user_registration.registration_handlers import UserRegistrationHandlers
from application.users.user_registration.services.registration_service import RegistrationService
from application.users.user_registration.usecases.check_user_registration import CheckUserRegistrationUseCase
from application.users.user_registration.usecases.validate_email import ValidateEmailUseCase
from application.users.user_registration.usecases.save_user import SaveUserUsecase
from application.companies.services.join_company_service import JoinCompanyService
from infrastructure.validators_impl.companies_validator import CompaniesValidatorImpl


usecases = UseCaseProviderImpl()

company_validator = CompaniesValidatorImpl()
companies_validator = CompaniesValidatorImpl()

join_company_service = JoinCompanyService(companies_validator=company_validator,
                                     repository_dependency_provider=repositroties_dependency_provider_async,
                                     usecases=usecases)

check_user_registration_usecase = CheckUserRegistrationUseCase(repositroties_dependency_provider_async.get_users_repository())
validate_email_usecase = ValidateEmailUseCase()
save_user_usecase = SaveUserUsecase(repositroties_dependency_provider_async.get_users_repository())

usecases = UseCaseProviderImpl(
    check_user_registration=check_user_registration_usecase,
    validate_email=validate_email_usecase,
    save_user=save_user_usecase
)

registration_service = RegistrationService(usecases)
handlers = UserRegistrationHandlers(registration_service, join_company_service)

user_registration_router = handlers.get_router()
