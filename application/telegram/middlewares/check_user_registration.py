from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable
from aiogram.types import TelegramObject, Message, CallbackQuery
from aiogram.exceptions import TelegramMigrateToChat, TelegramNetworkError
from aiogram.types import BotCommand
from db.postgresql_handlers.group_chat_db_handler import is_group_chat_in_company
from db.postgresql_handlers.users_db_handler import user_is_exists
from icecream import ic
import logging


class CheckRegistrationMiddleware(BaseMiddleware):
    """
    A class whose purpose is to check whether a user is registered in the database or not
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Checks whether a user is registered in the database

        :param handler: the function that is wrapped in this middleware
        :param event: the event that the user triggered
        :param data: the data that was passed to the handler

        :return: handler
        """
        
        self.user_id = data["event_from_user"].id
        self.chat_id = data["event_chat"].id
        # ic(handler)
        # ic(event)
        try:
            self.bot_commands = await event.bot.get_my_commands(request_timeout=40)
        except TelegramNetworkError as e:
            ic(str(e))
            self.bot_commands = [
                                BotCommand(command='main_menu', description='Открыть главное меню'),
                                BotCommand(command='add_chat_to_company', description='Добавить групповой чат в компанию'),
                                BotCommand(command='registration', description='Регистрация в боте')
                                ]
        self.bot_commands = ["/" + command.command for command in self.bot_commands]
        if isinstance(event, Message):
            if self.is_group_chat(self, data):
                await self.handle_group_chat(self, handler=handler, event=event, data=data)
            else:
                await self.handle_user_chat(self, handler=handler, event=event, data=data)
        elif isinstance(event, CallbackQuery):
            await self.handle_callback_queries(self, handler=handler, event=event, data=data)


    @staticmethod
    def is_group_chat(self, data):
        
        return str(data["event_chat"].id).startswith("-")

    @staticmethod
    async def handle_group_chat(self, handler, event, data):
        ic(event)
        if event.voice or event.video_note or event.document or event.video or event.audio:
            ic(handler)
            return await handler(event, data)

        if event.text and any(command in event.text for command in ['/add_chat_to_company']):
            return await handler(event, data)
        
        if (event.text and event.text in self.bot_commands and user_is_exists(user_id=self.user_id) and
                is_group_chat_in_company(chat_id=self.chat_id)):
            ic('/command в чате с компанией')
            return await handler(event, data)
        
        if event.text and event.text in self.bot_commands and not is_group_chat_in_company(chat_id=self.chat_id):
            ic('/command в чате без компании')
            await self.send_group_registration_message(event)
            return

        if event.text and 'ctrl' in event.text.lower():
            ic('ctrl')
            return await handler(event, data)

        text_to_check = event.text or event.caption
        ic(text_to_check)
        if text_to_check:
            if not any(word.lower() in text_to_check.lower() for word in ['ягодка', 'джарвел']):
                ic('не ягодка')
                return await handler(event, data)

            if isinstance(event, Message) and any(word in text_to_check.lower() for word in ['ягодка', 'джарвел']) and user_is_exists(user_id=self.user_id):
                ic('ягодка но пользователь зареган')
                ic(data)
                return await handler(event, data)
            

        # if event.text is not None:
        #     if not any(word.lower() in event.text.lower() for word in ['ягодка', 'джарвел']):
        #         ic('не ягодка')
        #         return await handler(event, data)

        #     if isinstance(event, Message) and any(word in event.text.lower() for word in ['ягодка', 'джарвел']) and user_is_exists(user_id=self.user_id):
        #         ic('ягодка но пользователь зареган')
        #         return await handler(event, data)

        if user_is_exists(user_id=self.user_id):
            ic("пользователь зареган")
            return await handler(event, data)
        if event.text is None:
            return
        ic('не пустили1')

        await self.send_user_registration_message(event)

    @staticmethod
    async def handle_user_chat(self, handler, event, data):
        if event.text:
            logging.debug(f"{event.from_user.id} ({event.from_user.username}): {event.text}")
        if user_is_exists(self.user_id):
            ic('существует')
            return await handler(event, data)
        else:
            if event.voice or event.video_note or event.document or event.video or event.photo or event.audio:
                ic('voice')
                return await handler(event, data)

            if event.text.startswith('/registration') or event.text.startswith('/start'):
                ic("регистрация или старт")
                return await handler(event, data)
            try:
                state_code = await data['state'].get_state()
                if state_code.startswith('Registration'):
                    ic("состояние регистрации")
                    return await handler(event, data)
            except Exception as e:
                pass
            ic('не пустили2')
            await self.send_user_registration_message(event)

    
    @staticmethod
    async def handle_callback_queries(self, handler, event, data):
        if event.data:
            ic("callback")
            return await handler(event, data)

    @staticmethod
    async def send_user_registration_message(event: TelegramObject):
        message_text = \
"""
Привет! Я - Джарвел, твой виртуальный помощник.
Чтобы я смог помочь тебе, нужно зарегистрироваться. 
Это просто: введи в личных сообщениях со мной команду /registration или команду /start, и я с радостью проведу тебя через этот процесс!

Я записал для тебя видео, как это делается. Обязательно посмотри его

"""
        file_id = "BAACAgIAAx0CfWptYgACD41mubXFrUKXkciPQKVkFtJyutupwgACD1IAAjN4qUmXcbLKm-gv7zUE"
        if isinstance(event, Message):
            try:
                await event.answer(message_text)
            except TelegramMigrateToChat as e:
                pass


    @staticmethod
    async def send_group_registration_message(event: TelegramObject):
        message_text = ("Для использования данной функции вам необходимо зарегистрировать данный чат в компании\n"
                        "Используйте команду /add_chat_to_company <Код компании>\n\n"
                        "Вставьте вместо <Код компании> код (без угловых скобок), который вы получили при создании компании")
        file_id = "BAACAgIAAx0CfWptYgACD49mubXzBJYvy--fI-dDHLz2jJKdQAACGlIAAjN4qUn10QJwUFS42jUE"
        if isinstance(event, Message):
            await event.answer(message_text)