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
    
    async def make_forward_tunneling(self, message: types.Message, tunneling_messages_from_db: TunnelingMessage) -> None:
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
            await self.make_send_tunneling(message, tunneling_messages_from_db)
        
    async def make_send_tunneling(self, message: types.Message, tunneling_messages_from_db: TunnelingMessage) -> None:
        if message.pinned_message:
            return
        bot = message.bot
        
        for tunneling_message_from_db in tunneling_messages_from_db:
            response_on_message = ''
            sended_message = None
            if message.reply_to_message:
                sended_message = True
                await bot.copy_message(chat_id=tunneling_message_from_db.to_chat_id, 
                    from_chat_id = tunneling_message_from_db.from_chat_id,
                    message_thread_id=tunneling_message_from_db.to_topic_id,
                    message_id = message.reply_to_message.message_id,
                ) 

            if sended_message:
                response_on_message = f"\nОтвет на {self.__get_link_from_message(sended_message)}"
            message_last_name = message.from_user.last_name if message.from_user.last_name else ''
            message_title = f'''Отправитель: <a href='https://t.me/{message.from_user.username}'>{message.from_user.first_name} {message_last_name}</a>\nВремя {self.__get_time(message)}''' + response_on_message
            await bot.send_message(tunneling_message_from_db.to_chat_id, message_title, message_thread_id=tunneling_message_from_db.to_topic_id, parse_mode="HTML", disable_web_page_preview=True)
            await bot.copy_message(chat_id=tunneling_message_from_db.to_chat_id, 
                    from_chat_id = tunneling_message_from_db.from_chat_id,
                    message_thread_id=tunneling_message_from_db.to_topic_id,
                    message_id = message.message_id,
                ) 

    def __get_link_from_message(self, message):
        if message.message_thread_id:
            return f"https://t.me/c/{str(message.chat.id).replace('-100', '')}/{message.message_thread_id}/{message.message_id}"
        if "-" in str(message.chat.id) and len(str(message.chat.id)) == 11:
            return f"https://t.me/c/{message.chat.id}/{message.message_id}"
        return f"https://t.me/c/{str(message.chat.id).replace('-100', '')}/{message.message_id}"

    
    def __get_time(self, message) -> datetime:
        utc_datetime = message.date
        MOSCOW_TZ = ZoneInfo("Europe/Moscow")
        moscow_datetime = utc_datetime.astimezone(MOSCOW_TZ)
        formatted_datetime = moscow_datetime.strftime('%H:%M:%S %Y-%m-%d')
        return formatted_datetime