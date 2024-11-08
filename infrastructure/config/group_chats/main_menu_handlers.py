from application.telegram.handlers.group_chats.menu.main_page_handlers import GroupMenuMainPageHandlers
from application.telegram.group_chat_menu.services.main_page_service import MainPageService
from infrastructure.config.repository_provider_async_config import repositroties_dependency_provider_async
from infrastructure.config.assistants.task_assistant_config import task_assistant
from infrastructure.config.assistants.mailing_assistant_config import mailing_assistant
from infrastructure.config.assistants.meeting_assistant_config import meeting_assistant


main_menu_service = MainPageService(task_assistant=task_assistant,
                                    mailing_assistant=mailing_assistant,
                                    meeting_assistant=meeting_assistant,
                                    repository_provider=repositroties_dependency_provider_async)

main_menu_handlers = GroupMenuMainPageHandlers(main_menu_service)

main_menu_router = main_menu_handlers.get_router()
