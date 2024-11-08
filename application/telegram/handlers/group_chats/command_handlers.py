from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from db.postgresql_handlers.companies_db_handler import get_code_owner_from_company, is_group_in_company_registered, \
    add_groups_chat_in_company
from infrastructure.config.repository_provider_async_config import companies_repository
from domain.entities.group_chat import GroupChat
from application.telegram.keyboards import group_chat_keyboards

router_commands = Router()
tag = "group_chats_command"


@router_commands.message(Command("add_chat_to_company"), F.chat.type != "private")
async def add_chat_to_company_command(message: Message, command: CommandObject):
    """
    Function processes the add_chat_to_company command
    Function saves information about the group chat in the database

    :param Message message: Object represents a message from Telegram
    :param Command command: Object represents a set of words sent by users after a command in a single message

    :return: None
    """
    chat_id = message.chat.id
    chat_name = message.chat.full_name
    user_id = message.from_user.id

    company_code = command.args

    if not company_code:
        await message.reply(
            f"Для добавления чата в команию введите команду в формате /add_chat_to_company <код коллектива> (без угловых скобок)"
        )
        return

    data = get_code_owner_from_company(company_code)

    if not data:
        await message.reply(f"Компании с кодом {company_code} не найдено!")
        return
    gc = GroupChat(chat_id=chat_id,
                   company_code=company_code,
                   name=message.chat.full_name)
    is_group_in_company_registered = await companies_repository.is_group_registered_in_company(gc)
    if is_group_in_company_registered:
        await message.reply("Чат уже добавлен в компанию!")
        return

    await companies_repository.add_group_chat_to_company(gc)

    await message.reply("Чат добавлен в компанию!")
