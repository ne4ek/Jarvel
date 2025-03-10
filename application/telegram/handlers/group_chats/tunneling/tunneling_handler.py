from aiogram import types, Router, F
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from db.postgresql_handlers.companies_db_handler import get_code_owner_from_company
from infrastructure.providers_impl.repositories_provider_async_impl import RepositoriesDependencyProviderImplAsync
from application.tunneling.tunneling_message_service import TunnelingMessageService
from domain.entities.group_chat import GroupChat
from icecream import ic
from aiogram.exceptions import TelegramBadRequest
from domain.entities.tunneling_message import TunnelingMessage
class TunnelStateStart(StatesGroup):
    waiting_for_link = State()

class TunnelStateStop(StatesGroup):
    waiting_for_link = State()
import re

class TunnelingHandler:
    def __init__(self, repository_provider: RepositoriesDependencyProviderImplAsync, tunneling_message_service: TunnelingMessageService) -> None:
        self.repository_provider = repository_provider
        self.tunneling_repository = repository_provider.get_tunneling_repository()
        self.tunneling_message_service = tunneling_message_service
    
    def get_router(self):
        router = Router()
        self.__register_callbacks(router)
        self.__register_command(router)
        self.__register_state(router)
        return router
    
    def __register_callbacks(self, router: Router) -> None:
        router.callback_query.register(self.send_f_message_callback, F.data.startswith("send_tunnel_f"))
        router.callback_query.register(self.send_message_callback, F.data.startswith("send_tunnel"))

            
    def __register_command(self, router: Router) -> None:
        router.message(Command("tunnel"), F.chat.type != "private")(self.tunnel_start)
        router.message(Command("stop_tunnel"), F.chat.type != "private")(self.stop_tunnel_start)
        router.message(Command("send"), F.chat.type != "private")(self.send_command_start)
        router.message(Command("send_f"), F.chat.type != "private")(self.send_f_command_start)

    def __register_state(self, router: Router) -> None:
        router.message(TunnelStateStart.waiting_for_link, F.chat.type != "private")(self.tunnel_waiting_for_chat_link)
        router.message(TunnelStateStop.waiting_for_link, F.chat.type != "private")(self.stop_tunnel_waiting_for_chat_link)
    
    async def tunnel_start(self, message: Message, state: FSMContext):
        await message.reply("Отправьте ссылку на чат.")
        await state.set_state(TunnelStateStart.waiting_for_link)

    async def tunnel_waiting_for_chat_link(self, message: Message, state: FSMContext):
        link = message.text.strip()
        if not self.is_telegram_link(link):
            await message.reply("Это не выглядит как ссылка на чат.")
        else:
            bot = message.bot
            to_chat_id, to_topic_id = self.__get_chat_topik_id_from_link(link)
            from_chat_id = int("-" + str(abs(message.chat.id)))
            from_topic_id = message.message_thread_id 
            tunneling_message = TunnelingMessage(to_chat_id=to_chat_id, to_topic_id=to_topic_id,
                            from_chat_id=from_chat_id, from_topic_id=from_topic_id) 
            tunneling_message_from_db = await self.tunneling_repository.get_by_full_info(tunneling_message)
            if tunneling_message_from_db:
                await message.reply("Туннель уже существует.")
            else:
                message_for_send_to_specify_chat = f'echo "HI tunnel started... successfully..." 🫡.\nFrom {self.get_telegram_link(from_chat_id, from_topic_id)}'
                try:
                    bot_sended_message_to_specify_chat = await bot.send_message(chat_id=to_chat_id, text=message_for_send_to_specify_chat, message_thread_id=to_topic_id)
                    tunneling_message.specify_chat_pinned_message_id = bot_sended_message_to_specify_chat.message_id
                    try:
                        await bot.pin_chat_message(chat_id=to_chat_id, message_id=bot_sended_message_to_specify_chat.message_id)
                    except TelegramBadRequest as tbr: pass
                except TelegramBadRequest as tbr:
                    message_for_send_to_source_chat = "Возникла ошибка при попытке связаться с указанным чатом."
                    await message.reply(message_for_send_to_source_chat)
                    ic(str(tbr))
                else:
                    await self.tunneling_repository.save(tunneling_message)
        await state.clear()
    
    def is_telegram_link(self, url: str):
        pattern = r"https://t\.me/[+\w\-_/]+"
        return re.match(pattern, url)
        
    async def stop_tunnel_start(self, message: Message, state: FSMContext):
        text = "Отправьте ссылку на чат, в которй хотите прекратить туннелирование."
        await message.reply(text)
        await state.set_state(TunnelStateStop.waiting_for_link)

    async def stop_tunnel_waiting_for_chat_link(self, message: Message, state: FSMContext):
        link = message.text.strip()
        if not self.is_telegram_link(link):
            await message.reply("Это не выглядит как ссылка на чат.")
        else:
            bot = message.bot
            to_chat_id, to_topic_id = self.__get_chat_topik_id_from_link(link)
            from_chat_id = int("-" + str(abs(message.chat.id)))
            from_topic_id = message.message_thread_id 
            tunneling_message = TunnelingMessage(to_chat_id=to_chat_id, to_topic_id=to_topic_id,
                            from_chat_id=from_chat_id, from_topic_id=from_topic_id)
            tunneling_message_from_db = await self.tunneling_repository.get_by_full_info(tunneling_message) 
            if not tunneling_message_from_db:
                await message.reply("Туннеля не существует.")
            else:
                await self.tunneling_repository.delete_by_full_info(tunneling_message)
                sourse_chat_link = self.get_telegram_link(tunneling_message_from_db.from_chat_id, tunneling_message_from_db.from_topic_id)
                text_for_listener_chat = f"Туннелирование из чата {sourse_chat_link} было прекращено."
                listener_chat_link = self.get_telegram_link(tunneling_message_from_db.to_chat_id, tunneling_message_from_db.to_topic_id)
                text_for_source_chat = f"Туннелирование в чат {listener_chat_link} было прекращено."
                await message.reply(text_for_source_chat)
                try:
                    await bot.send_message(tunneling_message_from_db.to_chat_id, text_for_listener_chat, message_thread_id=tunneling_message_from_db.to_chat_id)
                except TelegramBadRequest as tbr: pass
                try:
                    await bot.unpin_chat_message(chat_id=tunneling_message_from_db.from_chat_id, message_id=tunneling_message_from_db.source_chat_pinned_message_id)
                except TelegramBadRequest: ic("trable with unpining in specify chat")
                try:
                    await bot.unpin_chat_message(chat_id=tunneling_message_from_db.to_chat_id, message_id=tunneling_message_from_db.specify_chat_pinned_message_id)
                except TelegramBadRequest: pass
        await state.clear()

    def get_telegram_link(self, chat_id: int, topic_id: int|None) -> str:
        if topic_id is None:
            topic_id = ''
        elif topic_id == 0:
            topic_id = 1
        return f"https://t.me/c/{str(chat_id).replace('-100', '')}/{topic_id}"

    def __get_chat_topik_id_from_link(self, link: str) -> tuple[str]:
        splited_link = link.split("/")
        if splited_link[-2].isdigit():
            chat_id = int("-100" + splited_link[-2])
            topic_id = int(splited_link[-1])
            if topic_id == 1:
                topic_id = 0
        else:
            if '-' in splited_link[-1] and len(splited_link[-1]) == 11:
                chat_id = int(splited_link[-1])
            else:
                chat_id = int("-100" + splited_link[-1])
            topic_id = None
        return (chat_id, topic_id)
    
    async def send_command_start(self, message: Message):
        await self.__send_command_base(message, "send_tunnel")

    async def send_f_command_start(self, message: Message):
        await self.__send_command_base(message, "send_tunnel_f")
        
    async def __send_command_base(self, message: Message, tunnelig_type: str): 
        if not message.reply_to_message:
            text = "Вы должны ответить(reply) на сообщение, которое хотите отправить."
            await message.reply(text)
            return 
        chat_id = message.chat.id
        connected_chats = await self.tunneling_repository.get_full_by_chat_id(chat_id)
        response = await self.__get_response_for_send_command(message, connected_chats, tunnelig_type)
        await message.reply(response["text"], reply_markup=response["keyboard"])  
        
    async def __get_response_for_send_command(self, message: Message, connected_chats: tuple[list[TunnelingMessage]], tunnelig_type: str) -> dict:
        response = {"text": None, "keyboard": None}
        bot = message.bot
        text_list = []
        inline_keyboard = []
        connected_chats_to = connected_chats[0]
        connected_chats_from = connected_chats[1]
        i = 0
        for connected_chat_to in connected_chats_to:
            chat = await bot.get_chat(chat_id=connected_chat_to.to_chat_id)
            chat_title = chat.title
            text_list.append(f"{i + 1} - {chat_title}")
            inline_keyboard.append([InlineKeyboardButton(text=f"{i+1}", callback_data=f"{tunnelig_type} {connected_chat_to.to_chat_id} {connected_chat_to.to_topic_id} {message.reply_to_message.message_id}")])
            i += 1
        for connected_chat_from in connected_chats_from:
            chat = await bot.get_chat(chat_id=connected_chat_from.from_chat_id)
            chat_title = chat.title
            text_list.append(f"{i + 1} - {chat_title}")
            inline_keyboard.append([InlineKeyboardButton(text=f"{i+1}", callback_data=f"{tunnelig_type} {connected_chat_from.from_chat_id} {connected_chat_from.from_topic_id} {message.reply_to_message.message_id}")])
            i += 1
        text = "Чатов не найдено." if not text_list else '\n'.join(text_list)
        response["text"] = text
        response["keyboard"] = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        return response    
    
    async def send_f_message_callback(self, callback):
        bot = callback.message.bot
        chat_id, from_chat_id, topic_id, message_id = await self.__send_base_message_callback(callback)
        await bot.forward_message(chat_id=chat_id, from_chat_id=from_chat_id, message_thread_id=topic_id, message_id = message_id)
        await callback.message.reply("Отправлено")
        
    async def send_message_callback(self, callback):
        bot = callback.message.bot
        chat_id, from_chat_id, topic_id, message_id = await self.__send_base_message_callback(callback)
        await bot.copy_message(chat_id=chat_id, from_chat_id=from_chat_id, message_thread_id=topic_id, message_id = message_id)
        await callback.message.reply("Отправлено")
    
    async def __send_base_message_callback(self, callback):
        await callback.answer()
        callback_data_splited = callback.data.split()
        chat_id = int(callback_data_splited[1])
        if callback_data_splited[2] == "None":
            topic_id = None
        else:
            topic_id = int(callback_data_splited[2])
        message_id = int(callback_data_splited[3])
        return (chat_id, callback.message.chat.id, topic_id, message_id)