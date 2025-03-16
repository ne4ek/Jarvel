from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from zoneinfo import ZoneInfo
from aiogram.enums import ParseMode
from application.messages.custom_errors.duration_error import DurationTooLongError
from application.messages.services.message_service import TelegramMessageService
from application.messages.message_transcriber import audio_to_text_converter
from application.tunneling.tunneling_message_service import TunnelingMessageService
from infrastructure.providers_impl.repositories_provider_async_impl import RepositoriesDependencyProviderImplAsync
from domain.entities.tunneling_message import TunnelingMessage
from domain.entities.transcribed_message import TranscribedMessage
from const import PHRASES_FOR_IGNORE_MESSAGE 
from icecream import ic
from aiogram.exceptions import TelegramBadRequest
import re
import os

class ProcessMessageHandlers:
    def __init__(self, message_service: TelegramMessageService, repository_provider: RepositoriesDependencyProviderImplAsync, tunneling_message_service: TunnelingMessageService):
        self.message_service = message_service
        self.repository_provider = repository_provider
        self.tunneling_message_service = tunneling_message_service
        self.tunneling_repository = repository_provider.get_tunneling_repository()
        self.media_group_repository = repository_provider.get_media_group_repository()
        
    def get_router(self):
        router = Router()
        self.register_handlers(router)
        return router

    def register_handlers(self, router: Router):
        router.message(F.chat.type != "private", self._async_filter(self.tunneling_is_on))(self.message_handler)
        router.message(F.chat.type != "private", F.func(self.ignore_message))(self.ignore_message_handler)
        router.message(F.chat.type != "private", F.func(self.contains_ctrl_in_words))(self.ctrl_message_handler)
        router.message(F.chat.type != "private", F.func(self.contains_up_in_words))(self.up_message_handler)
        router.message(F.chat.type != "private", F.func(self.contains_vipolnil_in_words))(self.up_ready_handler)
        router.message(F.chat.type != "private")(self.message_handler)

    def _async_filter(self, coro_func):
        async def wrapped(*args, **kwargs):
            return await coro_func(*args, **kwargs)
        return wrapped
    
    def ignore_message(self, message: types.Message) -> bool:
        for phrase in PHRASES_FOR_IGNORE_MESSAGE:
            if phrase in message.text:
                return True
        return False
    
    async def ignore_message_handler(self, message: types.Message):
        return
    
    async def tunneling_is_on(self, message: types.Message, **kwargs) -> bool:
        tunneling_message = TunnelingMessage(from_chat_id=message.chat.id, from_topic_id=self.__get_topic_id(message))
        tunneling_messages_from_db = await self.tunneling_repository.get_by_from_info(tunneling_message)
        if not tunneling_messages_from_db:
            return False
        await self.__make_tunneling(message)
        return False

    def __get_topic_id(self, message: types.Message) -> int | None:
        return message.message_thread_id if message.chat.is_forum else None


    async def __make_tunneling(self, message: types.Message):
        ic("tunneling_is_on")
        tunneling_message = TunnelingMessage(from_chat_id=message.chat.id, from_topic_id=self.__get_topic_id(message))
        tunneling_messages_from_db = await self.tunneling_repository.get_by_from_info(tunneling_message)
        try:
            await self.tunneling_message_service.make_forward_tunneling(message, tunneling_messages_from_db)
        except TelegramBadRequest as tbr:
            await self.tunneling_message_service.make_send_tunneling(message, tunneling_messages_from_db)

    async def __make_simple_send_tunneling(self, message: types.Message, tunneling_messages_from_db: TunnelingMessage, text, reply_markup):
        bot = message.bot
        for tunneling_message_from_db in tunneling_messages_from_db:
            await bot.send_message(chat_id=tunneling_message_from_db.to_chat_id, 
                        message_thread_id=tunneling_message_from_db.to_topic_id,
                        text = text, 
                        reply_markup = reply_markup,
                        ) 

    def contains_up_in_words(self, message: types.Message) -> bool:
        pattern = re.compile(r'\bап\b.*(?:@\w+)+', re.IGNORECASE)
        if not message.text:
            return False
        return  bool(pattern.search(message.text))
    
    def contains_ctrl_in_words(self, message: types.Message) -> bool:
        if not message.text:
            return False
        words = message.text.lower().split()
        return "ctrl" in words
    
    def contains_vipolnil_in_words(self, message: types.Message) -> bool:
        if not message.text:
            return False
        words = message.text.lower().split()
        return "выполнил" in words
    
    
    async def ctrl_message_handler(self, message: types.Message):
        ic("ctrl_message_handler")
        if message.forward_from:
            return
        text = message.text
        if message.reply_to_message:
            replyed_message = message.reply_to_message
            text = f"@{replyed_message.from_user.username}  {replyed_message.text} {text}"
        bot = await message.bot.get_me()
        bot_username = bot.username
        sender_username = "@" + message.from_user.username
        message_id = message.message_id
        chat_id = message.chat.id
        ctrl_result = await self.message_service.process_ctrl(message_id, chat_id, text, bot_username, sender_username)
        
        if not ctrl_result:
            return
        await message.reply(ctrl_result)

    @audio_to_text_converter
    async def message_handler(self, message: TranscribedMessage | types.Message, state: FSMContext):
        message_text = message.text or message.caption
        if message_text:
            await self.message_service.save_message(message)
            if not self.message_service.is_bot_mentioned(message_text):
                return
                
            bot_message = await message.reply(text="Обрабатываю запрос...")
            response: dict = await self.message_service.call_assistant(bot_message, message, state)
            try:
                if response:
                    parse_mode = response.get("parse_mode") if "parse_mode" in response.keys() else ParseMode.HTML
                else:
                    parse_mode = ParseMode.HTML
                bot_message = await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"), parse_mode=parse_mode)
                await self.message_service.save_message(bot_message)
                if isinstance(message, TranscribedMessage):  
                    tunneling_message = TunnelingMessage(from_chat_id=message.chat.id, from_topic_id=self.__get_topic_id(message.original_message))
                else:
                    tunneling_message = TunnelingMessage(from_chat_id=message.chat.id, from_topic_id=self.__get_topic_id(message))
                tunneling_message_from_db = await self.tunneling_repository.get_by_from_info(tunneling_message)
                if tunneling_message_from_db:
                    await self.__make_simple_send_tunneling(message, tunneling_message_from_db, text=response.get("message"), reply_markup=response.get("keyboard"))
            except TelegramBadRequest as tbr:
                await bot_message.edit_text(text="Ошибка обработки сообщения")
                raise tbr     
            except Exception as e:
                await bot_message.edit_text(text="Ошибка обработки сообщения")
                raise e
                    
    async def up_message_handler(self, message: types.Message):
        ic("up_message_handler")
        up_result = await self.message_service.process_up(message)
        if up_result:
            await message.reply(up_result)
        
    async def up_ready_handler(self, message: types.Message):
        ic("up_ready_handler")
        up_ready_result = await self.message_service.process_ready_up(message)
        ic(up_ready_result)
        if up_ready_result:
            await message.reply(up_ready_result)

                
