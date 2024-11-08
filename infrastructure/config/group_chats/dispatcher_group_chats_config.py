#from infrastructure.config.tasks_config import tg_save_task_controller
from aiogram import Dispatcher, F

from application.telegram.handlers.group_chats.interface.main_menu import menu_gc_main_callback, \
    menu_group_chat_refactor_callback, group_chat_delete_company_from_group_chat, menu_group_chat_info_callback


def config(dp: Dispatcher):
    #messages.register_handlers(dp, message_service, 
    #                           transcribe_message_usecase,
    #                           summarize_message_usecase,
    #                           ctrl_message_usecase,
    #                           distributor)
    #register_callbacks(dp)
    include_routers(dp)



def include_routers(dp: Dispatcher):
    from application.telegram.handlers.group_chats.initialization import group_chats_router
    dp.include_router(group_chats_router)


def register_callbacks(dp: Dispatcher):
    """
    Функция регистрирует все callback для групповых чатов
    """
    #dp.callback_query.register(menu_gc_main_callback,
    #                           F.data == "group_go_to main_menu")

    #register_meetings(dp)
    #register_chat_info(dp)
    #register_refactor_chat(dp)


def register_refactor_chat(dp: Dispatcher):
    dp.callback_query.register(menu_group_chat_refactor_callback,
                               F.data == "group_go_to menu_refactor_chat")

    dp.callback_query.register(group_chat_delete_company_from_group_chat,
                               F.data == "group_delete_company_from_chat")


def register_chat_info(dp: Dispatcher):
    dp.callback_query.register(menu_group_chat_info_callback,
                               F.data == "group_go_to menu_chat_info")
