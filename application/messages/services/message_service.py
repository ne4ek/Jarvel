from aiogram import types
from aiogram.fsm.context import FSMContext
from typing import Union, List
from application.providers.usecases_provider import UseCasesProvider
from application.providers.repositories_provider import RepositoriesDependencyProvider
from domain.entities.transcribed_message import TranscribedMessage
from domain.entities.message import Message
from ai.assistants.distributor.distributor import Distributor
from ai.assistants.talker.talker import Talker
from ai.arbitrary_data_manager.arbitrary_data_manager import ArbitraryDataManager
from domain.entities.transcribed_message import TranscribedMessage
from domain.entities.group_chat import GroupChat
from icecream import ic
import re
import html

class TelegramMessageService:
    def __init__(self, repository_provider: RepositoriesDependencyProvider, usecases: UseCasesProvider, distributor: Distributor):
        self.message_repository = repository_provider.get_messages_repository()
        self.user_repository = repository_provider.get_users_repository()
        self.company_repository = repository_provider.get_companies_repository()
        self.group_chat_repository = repository_provider.get_group_chats_repository()
        self.usecases = usecases
        self.distributor = distributor


    async def process_ctrl(self, message_id: int, chat_id: int, text: str, bot_username: str, sender_username: str):
        return await self.usecases.ctrl_message_usecase.execute(text, message_id, chat_id, bot_username, sender_username)
    
    async def process_up(self, message: Message):
        return await self.usecases.up_message_usecase.execute(message)
    
    async def process_ready_up(self, message: Message):
        ic("process_ready_up")
        return await self.usecases.up_message_usecase.execute_ready_up(message)

    def is_bot_mentioned(self, text):
        return self.usecases.is_bot_mentioned.execute(text)

    async def call_assistant(self, bot_message: types.Message, user_message: Union[TranscribedMessage, types.Message], state: FSMContext):
        reply_message = user_message.reply_to_message
        sender_name = await self.__get_message_sender_full_name(user_message.from_user.id)
        if reply_message and reply_message.from_user.id == user_message.bot.id:
            messages = [
                {"role": "assistant", "content": f"Д: {reply_message.text}"},
                {"role": "user", "content": f"П ({sender_name}): {user_message.text}"}
            ]
        elif reply_message:
            reply_user_full_name = await self.__get_message_sender_full_name(reply_message.from_user.id)
            messages = [
                {"role": "user", "content": f"П ({reply_user_full_name}): {reply_message.text}"},
                {"role": "user", "content": f"П ({sender_name}): {user_message.text}"}
            ]
        else:
            messages = [
                {"role": "user", "content": f"П ({sender_name}): {user_message.text}"}
            ]
        assistant = await self.distributor.get_assistant(messages)
        ic(assistant)
        if not assistant:
            return
        if isinstance(assistant, Talker):
            messages = await self.__generate_assistant_messages(bot_message.chat.id, bot_message.bot.id, 20)
            message_to_send = await assistant.get_response(messages, user_message)
        elif isinstance(assistant, ArbitraryDataManager):
            del messages[0]
            message_to_send = await assistant.execute_action(initial_messages=messages, user_id=user_message.from_user.id)
        else:
            company_code = await self.__get_company_code(user_message.chat.id)
            if not company_code:
                #this is a temporary solution
                await self.__add_group_chat_to_Belomorie(bot_message)
                # message = ("Для использования этой функции вам необходимо зарегистрировать данный чат в компании\n"
                #           "Используйте команду /add_chat_to_company")
                # return {"message": message, "keyboard": None, "parse_mode": None}
            job_entity = await assistant.get_all_parameters(messages=messages,
                                                            company_code=company_code)
            await state.update_data({str(job_entity.__class__.__name__).lower(): {"entity": job_entity, "message": bot_message}})
            message_to_send = assistant.compose_telegram_filling_message(job_entity)
        message_to_send["message"] = self.__convert_to_html(message_to_send["message"])
        return message_to_send

    async def summarize_text(self, text):
        return await self.usecases.summarize_message_usecase.execute(text)

    async def __get_message_sender_full_name(self, user_id: int):
        return await self.user_repository.get_full_name_by_id(user_id=user_id)

    async def __get_company_code(self, chat_id: int):
        return await self.company_repository.get_company_code_by_chat_id(chat_id)

    async def __get_message_entity(self, message: Union[TranscribedMessage, types.Message]):
        msg_text = message.text or message.caption
        msg = Message()
        msg.chat_message_id = message.message_id
        msg.author_id = message.from_user.id
        
        msg.company_code = await self.company_repository.get_company_code_by_chat_id(message.chat.id)
        msg.text =  msg_text
        msg.date = message.date
        msg.replied_message_id = message.reply_to_message.message_id if message.reply_to_message else None
        msg.chat_id = message.chat.id
        msg.message_id = message.message_id
        return msg

    async def __add_group_chat_to_Belomorie(self, message: types.Message):
        gc = GroupChat(chat_id=message.chat.id, name=message.chat.title , company_code="Belomorie")
        await self.company_repository.add_group_chat_to_company(gc)
        
    async def __generate_assistant_messages(self, chat_id: int, bot_id: int, n_messages: int):
        messages: List[Message] = await self.message_repository.get_n_last_messages_by_chat_id(chat_id=chat_id,
                                                                                         bot_id=bot_id,
                                                                                         n=n_messages)
        messages_for_assistant = []
        for message in messages:
            msg = {"role": None, "content": None}
            content = \
"""
message_id: {message_id}
respond_to_message_id: {respond_to_message_id}
user_name: {user_name}
message: {text}
"""
            if message.is_bot_message:
                user_name = "Ассистент Ягодка"
                msg["role"] = "assistant"
            elif message.author_user:
                msg["role"] = "user"
                user_name = message.author_user.full_name
            else:
                msg["role"] = "user"
                user_name = "Неизвестный Пользователь"
            msg["content"] = content.format(message_id=message.message_id,
                                            respond_to_message_id=message.replied_message_id,
                                            user_name=user_name,
                                            text=message.text)
            messages_for_assistant.append(msg)
        messages_for_assistant.reverse()
        return messages_for_assistant

    def __convert_to_html(self, text: str):
        if not text:
            return
        
        tags_to_escape = [
        '<!DOCTYPE',
        '<html',
        '<head',
        '<body',
        '<script',
        '<style'
    ]
    
        for tag in tags_to_escape:
            escaped_tag = html.escape(tag)
            text.replace(tag, escaped_tag)
        
        text = re.sub(r'^(.*)\n={2,}$', r'<h1>\1</h1>', text, flags=re.MULTILINE)
        text = re.sub(r'^(.*)\n-{2,}$', r'<h2>\1</h2>', text, flags=re.MULTILINE)

        text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)

        text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)

        text = re.sub(r'(?m)^\- (.*)$', r'<li>\1</li>', text)

        text = re.sub(r'(?s)(<li>.*?</li>)', r'<ul>\1</ul>', text)
        allowed_tags = [
            'b', 'strong', 'i', 'em', 'code', 's', 'strike', 'del', 'u', 'pre'
        ]
        tag_pattern = re.compile(r'</?(\w+)[^>]*>|<![^>]*>')
        def replace_tag(match):
            tag = match.group(1)
            if tag in allowed_tags:
                return match.group(0)
            else:
                return html.escape(match.group(0))
        escaped_message = tag_pattern.sub(replace_tag, text)
        return escaped_message


    async def save_message(self, message: Union[TranscribedMessage, types.Message]):
        message_entity = await self.__get_message_entity(message)
        await self.message_repository.save(message_entity)
        
    async def shorten_text(self, text_for_shorting):
        return await self.distributor.shorten_message(text_for_shorting)