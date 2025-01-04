from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from application.messages.services.up_job_service import UpJobService
from application.messages.usecases.send_up_message_usecase import SendUpUseCase
from infrastructure.config.bot_config import bot
from .scheduler import scheduler_service

send_up_usecase = SendUpUseCase(bot, repositories=repositroties_dependency_provider_async)
up_job_service = UpJobService(repositories=repositroties_dependency_provider_async,
                                  scheduler_service=scheduler_service,
                                  send_up_usecase=send_up_usecase)