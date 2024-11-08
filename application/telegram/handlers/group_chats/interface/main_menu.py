from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from application.telegram.bot_msg.group_chat import group_chat_info_text
from application.telegram.keyboards import group_chat_keyboards
from db.postgresql_handlers.companies_db_handler import get_company_name_from_company, \
    get_company_code_from_group_chat, get_owner_company_name_by_company_code, get_description_from_company, \
    get_participants_names_from_company_by_company_code

from db.postgresql_handlers.group_chat_db_handler import get_group_chat_name, delete_company_from_group_chat


async def menu_gc_main_callback(callback: CallbackQuery, state: FSMContext):
    """
    Функция выводит главное меню

    :param CallbackQuery callback:
    :param FSMContext state:
    :return: None
    """

    await state.clear()

    await callback.message.edit_text(text="Главное меню",
                                     reply_markup=group_chat_keyboards.get_menu_main())


async def menu_group_chat_info_callback(callback: CallbackQuery, state: FSMContext):
    """
    Функция выводить всю информацию о групповом чате
    :param CallbackQuery callback:
    :param FSMContext state:
    :return: None
    """
    text = compose_group_chat_info(callback.message.chat.id)
    await callback.message.edit_text(text=text, parse_mode=ParseMode.HTML,
                                     reply_markup=group_chat_keyboards.get_menu_group_chat_info())


def compose_group_chat_info(group_chat_id):
    company_code = get_company_code_from_group_chat(group_chat_id)
    text = group_chat_info_text.format(
        chat_name=get_group_chat_name(group_chat_id),
        company_name=get_company_name_from_company(company_code),
        company_code=company_code,
        description=get_description_from_company(company_code),
        company_owner=get_owner_company_name_by_company_code(company_code),
        participants=get_participants_names_from_company_by_company_code(company_code),
    )
    return text


async def menu_group_chat_refactor_callback(callback: CallbackQuery, state: FSMContext):
    """
    Функция выводит меню изменения параметров чата
    :param CallbackQuery callback:
    :param FSMContext state:
    :return: None
    """

    text = "В этом меню вы можете изменить параметры этого чата"
    await callback.message.edit_text(text=text,
                                     reply_markup=group_chat_keyboards.get_menu_group_chat_refactor())


async def group_chat_delete_company_from_group_chat(callback: CallbackQuery, state: FSMContext):
    """
    Функция обрабатывает удаление компании из чата
    :param CallbackQuery callback:
    :param FSMContext state:
    :return: None
    """
    delete_company_from_group_chat(chat_id=callback.message.chat.id)
    text = "Удаление прошло успешно"
    await callback.message.edit_text(text=text,
                                     reply_markup=group_chat_keyboards.get_after_delete_company_from_chat_keyboard())