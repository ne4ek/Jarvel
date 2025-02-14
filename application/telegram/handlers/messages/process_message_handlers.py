from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from zoneinfo import ZoneInfo
from aiogram.enums import ParseMode
from application.messages.custom_errors.duration_error import DurationTooLongError
from application.messages.services.message_service import TelegramMessageService
from application.messages.message_transcriber import audio_to_text_converter
from infrastructure.providers_impl.repositories_provider_async_impl import RepositoriesDependencyProviderImplAsync
from domain.entities.tunneling_message import TunnelingMessage
from domain.entities.transcribed_message import TranscribedMessage
from icecream import ic
from aiogram.exceptions import TelegramBadRequest
import re
from const import TITLE_TEMPLATE_FOR_SEND_TUNNELING
import os
from datetime import datetime
import pytz

class ProcessMessageHandlers:
    def __init__(self, message_service: TelegramMessageService, repository_provider: RepositoriesDependencyProviderImplAsync):
        self.message_service = message_service
        self.repository_provider = repository_provider
        self.tunneling_repository = repository_provider.get_tunneling_repository()
        self.media_group_repository = repository_provider.get_media_group_repository()
        
    def get_router(self):
        router = Router()
        self.register_handlers(router)
        return router

    def register_handlers(self, router: Router):
        router.message(F.chat.type != "private", self._async_filter(self.tunneling_is_on))(self.message_handler)
        router.message(F.chat.type != "private", F.func(self.contains_ctrl_in_words))(self.ctrl_message_handler)
        router.message(F.chat.type != "private", F.func(self.contains_up_in_words))(self.up_message_handler)
        router.message(F.chat.type != "private", F.func(self.contains_vipolnil_in_words))(self.up_ready_handler)
        router.message(F.chat.type != "private")(self.message_handler)

    def _async_filter(self, coro_func):
        async def wrapped(*args, **kwargs):
            return await coro_func(*args, **kwargs)
        return wrapped
    
    async def tunneling_is_on(self, message: types.Message, **kwargs) -> bool:
        ic("tunneling_check")
        tunneling_message = TunnelingMessage(from_chat_id=message.chat.id, from_topic_id=message.message_thread_id)
        tunneling_messages_from_db = await self.tunneling_repository.get_by_from_info(tunneling_message)
        if not tunneling_messages_from_db:
            return False
        try:
            await self.__make_forward_tunneling(message, tunneling_messages_from_db)
        except TelegramBadRequest as tbr:
            await self.__make_send_tunneling(message, tunneling_messages_from_db)
        return False

    async def __make_forward_tunneling(self, message: types.Message, tunneling_messages_from_db: TunnelingMessage) -> None:
        bot = message.bot
        try:
            for tunneling_message_from_db in tunneling_messages_from_db:
                if message.reply_to_message:
                    await bot.forward_message(chat_id=tunneling_message_from_db.to_chat_id, 
                                        from_chat_id = tunneling_message_from_db.from_chat_id,
                                        message_thread_id=tunneling_message_from_db.to_topic_id,
                                        message_id = message.reply_to_message.message_id,
                                    )      
                await bot.forward_message(chat_id=tunneling_message_from_db.to_chat_id, 
                                        from_chat_id = tunneling_message_from_db.from_chat_id,
                                        message_thread_id=tunneling_message_from_db.to_topic_id,
                                        message_id = message.message_id,
                                    )
        except TelegramBadRequest as tbr:
            await self.__make_send_tunneling(message, tunneling_messages_from_db)
        
    async def __make_send_tunneling(self, message: types.Message, tunneling_messages_from_db: TunnelingMessage) -> None:
        if message.pinned_message:
            return
        bot = message.bot
        
        for tunneling_message_from_db in tunneling_messages_from_db:
            response_on_message = ''
            sended_message = None
            if message.reply_to_message and message.reply_to_message.text:
                await self.__reply_message_title_send(message, tunneling_message_from_db)
                sended_message = await self.__text_send(message.reply_to_message, tunneling_message_from_db)
            elif message.reply_to_message and message.reply_to_message.voice:
                await self.__reply_message_title_send(message, tunneling_message_from_db)
                sended_message = await self.__voice_send(message.reply_to_message, tunneling_message_from_db) 
            elif message.reply_to_message and message.reply_to_message.video_note:
                await self.__reply_message_title_send(message, tunneling_message_from_db)
                sended_message = await self.__video_note_send(message.reply_to_message, tunneling_message_from_db)
            elif message.reply_to_message and message.reply_to_message.document:
                await self.__reply_message_title_send(message, tunneling_message_from_db)
                sended_message = await self.__document_send(message.reply_to_message, tunneling_message_from_db)
            elif message.reply_to_message and message.reply_to_message.photo:
                await self.__reply_message_title_send(message, tunneling_message_from_db)
                sended_message = await self.__photo_send(message.reply_to_message, tunneling_message_from_db)   
            elif message.reply_to_message and message.reply_to_message.video:
                await self.__reply_message_title_send(message, tunneling_message_from_db)
                sended_message = await self.__video_send(message, tunneling_message_from_db)    

            if sended_message:
                response_on_message = f"\nОтвет на {self.__get_link_to_message(sended_message)}"
            message_last_name = message.from_user.last_name if message.from_user.last_name else ''
            message_title = f'''Отправитель: <a href='https://t.me/{message.from_user.username}'>{message.from_user.first_name} {message_last_name}</a>\nВремя {self.__get_time(message)}''' + response_on_message
            if not(message.media_group_id and await self.media_group_repository.is_exists(message.media_group_id)):
                await bot.send_message(tunneling_message_from_db.to_chat_id, message_title, message_thread_id=tunneling_message_from_db.to_topic_id, parse_mode="HTML", disable_web_page_preview=True)
            if message.text:
                await self.__text_send(message, tunneling_message_from_db, sended_message) 
            elif message.voice:
                await self.__voice_send(message, tunneling_message_from_db, sended_message)
            elif message.video_note:
                await self.__video_note_send(message, tunneling_message_from_db, sended_message)
            elif message.document:
                await self.__document_send(message, tunneling_message_from_db, sended_message)
            elif message.photo:
                await self.__photo_send(message, tunneling_message_from_db, sended_message)
            elif message.video:
                await self.__video_send(message, tunneling_message_from_db, sended_message)

    def __get_link_to_message(self, message):
        if message.message_thread_id:
            return f"https://t.me/c/{str(message.chat.id).replace('-100', '')}/{message.message_thread_id}/{message.message_id}"
        return f"https://t.me/c/{str(message.chat.id).replace('-100', '')}/{message.message_id}"

    async def __reply_message_title_send(self, message, tunneling_message):
        bot = message.bot
        reply_message_last_name = message.reply_to_message.from_user.last_name if message.reply_to_message.from_user.last_name else ''
        reply_message_title = f'''Отправитель: <a href='https://t.me/{message.reply_to_message.from_user.username}'>{message.reply_to_message.from_user.first_name} {reply_message_last_name}</a>\nВремя {self.__get_time(message.reply_to_message)}\n'''
        await bot.send_message(tunneling_message.to_chat_id, reply_message_title, message_thread_id=tunneling_message.to_topic_id, parse_mode="HTML", disable_web_page_preview=True)


    async def __text_send(self, message, tunneling_message, message_for_reply=None):
        bot = message.bot
        reply_to_message_id = None if not message_for_reply else message_for_reply.message_id 
        ic(reply_to_message_id)
        sended_message = await bot.send_message(chat_id=tunneling_message.to_chat_id, message_thread_id=tunneling_message.to_topic_id,text = message.text, reply_to_message_id=reply_to_message_id)
        return sended_message
            
    async def __voice_send(self, message, tunneling_message, message_for_reply=None):
        bot = message.bot
        reply_to_message_id = None if not message_for_reply else message_for_reply.message_id 
        sended_message = await bot.send_voice(tunneling_message.to_chat_id, message.voice.file_id, message_thread_id=tunneling_message.to_topic_id, reply_to_message_id=reply_to_message_id)
        return sended_message
    
    async def __video_note_send(self, message, tunneling_message, message_for_reply=None):
        bot = message.bot
        reply_to_message_id = None if not message_for_reply else message_for_reply.message_id
        sended_message = await bot.send_video_note(tunneling_message.to_chat_id, message.video_note.file_id, message_thread_id=tunneling_message.to_topic_id, reply_to_message_id=reply_to_message_id)
        return sended_message
    
    async def __document_send(self, message, tunneling_message, message_for_reply=None):
        bot = message.bot
        reply_to_message_id = None if not message_for_reply else message_for_reply.message_id
        sended_message = await bot.send_document(tunneling_message.to_chat_id, message.document.file_id, message_thread_id=tunneling_message.to_topic_id, reply_to_message_id=reply_to_message_id)
        return sended_message

    async def __photo_send(self, message, tunneling_message, message_for_reply=None):
        bot = message.bot
        reply_to_message_id = None if not message_for_reply else message_for_reply.message_id
        sended_message = await bot.send_photo(tunneling_message.to_chat_id, message.photo[-1].file_id, message_thread_id=tunneling_message.to_topic_id, reply_to_message_id=reply_to_message_id)
        return sended_message
    
    async def __video_send(self, message, tunneling_message, message_for_reply=None):
        bot = message.bot
        reply_to_message_id = None if not message_for_reply else message_for_reply.message_id
        sended_message = await bot.send_video(tunneling_message.to_chat_id, message.video.file_id, message_thread_id=tunneling_message.to_topic_id, reply_to_message_id=reply_to_message_id)
        return sended_message


    def __get_time(self, message) -> datetime:
        utc_datetime = message.date
        MOSCOW_TZ = ZoneInfo("Europe/Moscow")
        moscow_datetime = utc_datetime.astimezone(MOSCOW_TZ)
        formatted_datetime = moscow_datetime.strftime('%H:%M:%S %Y-%m-%d')
        return formatted_datetime

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
    async def message_handler(self, message: TranscribedMessage, state: FSMContext):
        message_text = message.text or message.caption
        if message_text:
            await self.message_service.save_message(message)
            if not self.message_service.is_bot_mentioned(message_text):
                return
                
            bot_message = await message.reply(text="Обрабатываю запрос...")
            response: dict = await self.message_service.call_assistant(bot_message, message, state)
            ic(response)
            try:
                if response:
                    parse_mode = response.get("parse_mode") if "parse_mode" in response.keys() else ParseMode.HTML
                else:
                    parse_mode = ParseMode.HTML
                ic(parse_mode)
                bot_message = await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"), parse_mode=parse_mode)
                await self.message_service.save_message(bot_message)
                ic(message)
                tunneling_message = TunnelingMessage(from_chat_id=message.chat.id, from_topic_id=message.original_message.message_thread_id)
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

                
