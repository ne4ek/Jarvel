from application.messages.usecases.ctrl_message_usecase import CtrlMessageUseCase
from application.messages.usecases.up_message_usecase import UpMessageUseCase
from application.messages.usecases.save_message import SaveMessageUseCase
from application.messages.usecases.summarize_message import SummarizeMessage
from application.messages.usecases.transcribe_voice_message import TranscribeTelegramMessage
from application.messages.usecases.is_bot_mentioned_usecase import IsBotMentionedUseCase
from application.messages.services.message_service import TelegramMessageService
from application.telegram.handlers.messages.process_message_handlers import ProcessMessageHandlers
from ai.summarization_prompts import summarization_prompt
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.providers_impl.usecases_provider_impl import UseCaseProviderImpl
from infrastructure.config.assistants.distributor_config import distributor
from const import VOICE_WORDS, BOT_MENTIONS
from .scheduler.ctrls_job_service import ctrl_job_service
from .scheduler.ups_job_service import up_job_service
import os




ctrl_message_usecase = CtrlMessageUseCase(repositories_provider=repositroties_dependency_provider_async,
                                          ctrl_job_service=ctrl_job_service)

up_message_usecase = UpMessageUseCase(up_job_service=up_job_service, 
                                      repositories_provider=repositroties_dependency_provider_async)

save_message_usecase = SaveMessageUseCase()
summarize_message_usecase = SummarizeMessage(model="gpt-4o-mini",
                                             api_key=os.getenv("GPT_API_KEY"),
                                             prompt=summarization_prompt,
                                             temperature=0)
is_bot_mentioned_usecase = IsBotMentionedUseCase(BOT_MENTIONS)
usecase_provider = UseCaseProviderImpl()

usecases_provider = UseCaseProviderImpl(is_bot_mentioned=is_bot_mentioned_usecase,
                                       save_message=save_message_usecase,
                                       summarize_message_usecase=summarize_message_usecase,
                                       ctrl_message_usecase=ctrl_message_usecase,
                                       up_message_usecase=up_message_usecase,)


message_service = TelegramMessageService(repository_provider=repositroties_dependency_provider_async,
                                         usecases=usecases_provider,
                                         distributor=distributor)

messages_handlers = ProcessMessageHandlers(message_service=message_service)

messages_router = messages_handlers.get_router()