from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from application.messages.services.ctrl_job_service import CtrlJobService
from application.messages.usecases.send_ctrl_message_usecase import SendCtrlUseCase
from infrastructure.config.bot_config import bot
from .scheduler import scheduler_service

send_ctrl_usecase = SendCtrlUseCase(bot)
ctrl_job_service = CtrlJobService(repositories=repositroties_dependency_provider_async,
                                  scheduler_service=scheduler_service,
                                  send_ctrl_usecase=send_ctrl_usecase)
