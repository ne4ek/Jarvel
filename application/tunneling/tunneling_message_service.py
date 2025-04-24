from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from datetime import datetime
from zoneinfo import ZoneInfo
from icecream import ic

from domain.entities.tunneling_message import TunnelingMessage
from const import TITLE_TEMPLATE_FOR_SEND_TUNNELING

class TunnelingMessageService:
    def __init__(self) -> None:
        pass
    
    async def tunnel(self, message: types.Message, tunneling_messages_from_db: list[TunnelingMessage]) -> None:
        await self.make_forward_tunneling(message, tunneling_messages_from_db)

    async def make_forward_tunneling(self, message: types.Message, tunneling_messages_from_db: TunnelingMessage) -> None:
        bot = message.bot
        try:
            for tunneling_message_from_db in tunneling_messages_from_db:
                if not tunneling_message_from_db.is_active:
                    continue
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
            await self.make_send_tunneling(message, tunneling_messages_from_db)
        
    async def make_send_tunneling(self, message: types.Message, tunneling_messages_from_db: TunnelingMessage) -> None:
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
            elif message.reply_to_message and message.reply_to_message.sticker:
                await self.__reply_message_title_send(message, tunneling_message_from_db)
                sended_message = await self.__sticker_send(message.reply_to_message, tunneling_message_from_db)

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
            elif message.sticker:
                await self.__sticker_send(message, tunneling_message_from_db, sended_message)

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

    async def __sticker_send(self, message, tunneling_message, message_for_reply=None):
        bot = message.bot
        reply_to_message_id = None if not message_for_reply else message_for_reply.message_id
        sended_message = await bot.send_sticker(tunneling_message.to_chat_id, message.sticker.file_id, message_thread_id=tunneling_message.to_topic_id, reply_to_message_id=reply_to_message_id)
        return sended_message
    
    def __get_time(self, message) -> datetime:
        utc_datetime = message.date
        MOSCOW_TZ = ZoneInfo("Europe/Moscow")
        moscow_datetime = utc_datetime.astimezone(MOSCOW_TZ)
        formatted_datetime = moscow_datetime.strftime('%H:%M:%S %Y-%m-%d')
        return formatted_datetime