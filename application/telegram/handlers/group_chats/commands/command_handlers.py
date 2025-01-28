from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from db.postgresql_handlers.companies_db_handler import get_code_owner_from_company, is_group_in_company_registered, \
    add_groups_chat_in_company
from application.telegram.keyboards import group_chat_keyboards

router_commands = Router()
tag = "group_chats_command"

#now it do not work (see application/telegram/handlers/group_chats/command_handlers.py)
@router_commands.message(Command("add_chat_to_company"), F.chat.type != "private")
async def add_chat_to_company_command(message: Message, command: CommandObject, state: FSMContext):
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

    if data[1] != user_id:
        await message.reply(
            "Только администратор компании может добавлять чаты в компанию!"
        )
        return

    if is_group_in_company_registered(chat_id, company_code):
        await message.reply("Чат уже добавлен в компанию!")
        return

    add_groups_chat_in_company(chat_id, chat_name, company_code, data[1])
    await message.reply("Чат добавлен в компанию!")


