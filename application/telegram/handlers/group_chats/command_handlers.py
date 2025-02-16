from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from db.postgresql_handlers.companies_db_handler import get_code_owner_from_company
from infrastructure.config.repository_provider_async_config import companies_repository, tunneling_repository
from domain.entities.group_chat import GroupChat
from icecream import ic
from aiogram.exceptions import TelegramBadRequest
from domain.entities.tunneling_message import TunnelingMessage

import re

router_commands = Router()

class AddChatToCompanyStates(StatesGroup):
    waiting_for_company_code = State()
    
class TunnelStateStart(StatesGroup):
    waiting_for_link = State()

class TunnelStateStop(StatesGroup):
    waiting_for_link = State()


@router_commands.message(Command("add_chat_to_company"), F.chat.type != "private")
async def add_chat_to_company_start(message: Message, state: FSMContext):
    chat_id = message.chat.id
    chat_name = message.chat.full_name
    is_group_in_company_registered = await companies_repository.get_company_code_by_chat_id(chat_id)

    if is_group_in_company_registered:
        await message.reply("Чат уже добавлен в компанию!")
        return

    await message.reply("Введите код компании для добавления чата\n(например: <code>Belomorie</code> ):", parse_mode="HTML")
    await state.set_state(AddChatToCompanyStates.waiting_for_company_code)

@router_commands.message(AddChatToCompanyStates.waiting_for_company_code, F.chat.type != "private")
async def add_chat_to_company_process(message: Message, state: FSMContext):
    company_code = message.text.strip()
    chat_id = message.chat.id
    chat_name = message.chat.full_name
    data = get_code_owner_from_company(company_code)
    if not data:
        await message.reply(f"Компании с кодом {company_code} не найдено! Попробуйте снова.")
        return
    gc = GroupChat(chat_id=chat_id, company_code=company_code, name=chat_name)
    await companies_repository.add_group_chat_to_company(gc)
    await message.reply("Чат добавлен в компанию!")
    await state.clear()

@router_commands.message(Command("registration"), F.chat.type != "private")
async def add_chat_to_company_start(message: Message, state: FSMContext):
    await message.reply("Регистрация проходит в личных сообщениях бота.")


@router_commands.message(Command("tunnel"), F.chat.type != "private")
async def tunnel_start(message: Message, state: FSMContext):
    await message.reply("Отправьте ссылку на чат.")
    await state.set_state(TunnelStateStart.waiting_for_link)


@router_commands.message(TunnelStateStart.waiting_for_link, F.chat.type != "private")
async def tunnel_waiting_for_chat_link(message: Message, state: FSMContext):
    link = message.text.strip()
    if not is_telegram_link(link):
        await message.reply("Это не выглядит как ссылка на чат.")
    else:
        bot = message.bot
        splited_link = link.split("/")
        if splited_link[-2].isdigit():
            to_chat_id = int("-100" + splited_link[-2])
            to_topic_id = int(splited_link[-1])
            if to_topic_id == 1:
                to_topic_id = 0
        else:
            to_chat_id = int("-100" + splited_link[-1])
            to_topic_id = None
        from_chat_id = int("-" + str(abs(message.chat.id)))
        from_topic_id = message.message_thread_id 
        tunneling_message = TunnelingMessage(to_chat_id=to_chat_id, to_topic_id=to_topic_id,
                         from_chat_id=from_chat_id, from_topic_id=from_topic_id) 
        tunneling_message_from_db = await tunneling_repository.get_by_full_info(tunneling_message)
        if tunneling_message_from_db:
            await message.reply("Туннель уже существует.")
        else:
            message_for_send_to_specify_chat = f'echo "HI tunnel started... successfully..." 🫡.\nFrom {get_telegram_link(from_chat_id, from_topic_id)}'
            try:
                bot_sended_message_to_specify_chat = await bot.send_message(chat_id=to_chat_id, text=message_for_send_to_specify_chat, message_thread_id=to_topic_id)
                try:
                    specify_chat_pinned_message = await bot.pin_chat_message(chat_id=to_chat_id, message_id=bot_sended_message_to_specify_chat.message_id)
                except TelegramBadRequest as tbr: pass
            except TelegramBadRequest as tbr:
                message_for_send_to_source_chat = "Возникла ошибка при попытке связаться с указанным чатом."
                await message.reply(message_for_send_to_source_chat)
                ic(str(tbr))
                tunneling_message.specify_chat_pinned_message_id = bot_sended_message_to_specify_chat.message_id
                await tunneling_repository.save(tunneling_message)
    await state.clear()
    
    

def is_telegram_link(url: str):
    pattern = r"https://t\.me/[+\w\-_/]+"
    return re.match(pattern, url)
    
    
# @router_commands.message(Command("stop_all_tunnel"), F.chat.type != "private")
# async def stop_all_tunel(message: Message, state: FSMContext):
#     tunneling_message = TunnelingMessage(from_chat_id=message.chat.id, from_topic_id=message.message_thread_id)
#     tunneling_messages_from_db = await tunneling_repository.get_by_from_info(tunneling_message=tunneling_message)
#     bot = message.bot
#     sourse_chat_link = get_telegram_link(tunneling_message.from_chat_id, tunneling_message.from_topic_id)
#     text_for_listener_chat = f"Тунелирование из чата {sourse_chat_link} было прекращено."
#     if tunneling_messages_from_db:
#         text_for_source_chat = "Туннелирование из этого чата в чаты:\n"
#         await tunneling_repository.delete_all_by_from(tunneling_message)
#         for tunneling_message_from_db in tunneling_messages_from_db:
#             try:
#                 await bot.send_message(chat_id=tunneling_message_from_db.to_chat_id, message_thread_id=tunneling_message_from_db.to_topic_id, text=text_for_listener_chat)
#                 try:
#                     await bot.unpin_chat_message(chat_id=tunneling_message_from_db.to_chat_id, message_id=tunneling_message_from_db.specify_chat_pinned_message_id)
#                 except TelegramBadRequest as tbr: pass
#             except TelegramBadRequest as tbr:
#                 ic(str(tbr))
#             text_for_source_chat += get_telegram_link(tunneling_message_from_db.to_chat_id, tunneling_message_from_db.to_topic_id) + "\n"
#         text_for_source_chat += "было прекращено."
#     else:
#         text_for_source_chat = "Этот чат не туннелируется."
#     await message.reply(text=text_for_source_chat)
#     try:
#         await bot.unpin_chat_message(chat_id=tunneling_message_from_db.from_chat_id, message_id=tunneling_message_from_db.source_chat_pinned_message_id)
#     except TelegramBadRequest as tbr: pass


@router_commands.message(Command("stop_tunnel"), F.chat.type != "private")
async def stop_tunnel_start(message: Message, state: FSMContext):
    text = "Отправьте ссылку на чат, в которй хотите прекратить туннелирование."
    await message.reply(text)
    await state.set_state(TunnelStateStop.waiting_for_link)

@router_commands.message(TunnelStateStop.waiting_for_link, F.chat.type != "private")
async def tunnel_waiting_for_chat_link(message: Message, state: FSMContext):
    link = message.text.strip()
    if not is_telegram_link(link):
        await message.reply("Это не выглядит как ссылка на чат.")
    else:
        bot = message.bot
        splited_link = link.split("/")
        if splited_link[-2].isdigit():
            to_chat_id = int("-100" + splited_link[-2])
            to_topic_id = int(splited_link[-1])
            if to_topic_id == 1:
                to_topic_id = 0
        else:
            to_chat_id = int("-100" + splited_link[-1])
            to_topic_id = None
        from_chat_id = int("-" + str(abs(message.chat.id)))
        from_topic_id = message.message_thread_id 
        tunneling_message = TunnelingMessage(to_chat_id=to_chat_id, to_topic_id=to_topic_id,
                         from_chat_id=from_chat_id, from_topic_id=from_topic_id)
        tunneling_message_from_db = await tunneling_repository.get_by_full_info(tunneling_message) 
        if not tunneling_message_from_db:
            await message.reply("Туннеля не существует.")
        else:
            await tunneling_repository.delete_by_full_info(tunneling_message)
            sourse_chat_link = get_telegram_link(tunneling_message_from_db.from_chat_id, tunneling_message_from_db.from_topic_id)
            text_for_listener_chat = f"Тунелирование из чата {sourse_chat_link} было прекращено."
            listener_chat_link = get_telegram_link(tunneling_message_from_db.to_chat_id, tunneling_message_from_db.to_topic_id)
            text_for_source_chat = f"Тунелирование в чат {listener_chat_link} было прекращено."
            await message.reply(text_for_source_chat)
            try:
                await bot.send_message(tunneling_message_from_db.to_chat_id, text_for_listener_chat, message_thread_id=tunneling_message_from_db.to_chat_id)
            except TelegramBadRequest as tbr: pass
            try:
                await bot.unpin_chat_message(chat_id=tunneling_message_from_db.from_chat_id, message_id=tunneling_message_from_db.source_chat_pinned_message_id)
            except TelegramBadRequest: ic("trable with unpining in specify chat")
            try:
                await bot.unpin_chat_message(chat_id=tunneling_message_from_db.to_chat_id, message_id=tunneling_message_from_db.specify_chat_pinned_message_id)
            except TelegramBadRequest: ic("trable with unpining in source chat")
    await state.clear()


def get_telegram_link(chat_id: int, topic_id: int) -> str:
    if topic_id is None:
        topic_id = ''
    elif topic_id == 0:
        topic_id = 1
    return f"https://t.me/c/{str(chat_id).replace('-100', '')}/{topic_id}"