import json
from datetime import datetime, timedelta
import pytz
from application.mailing.services.mail_scheduler_job_service import MailingJobService
from application.providers.repositories_provider import RepositoriesDependencyProvider
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from domain.contracts.assistant import Assistant
from domain.entities.transcribed_message import TranscribedMessage
from domain.entities.mail import Mail
from typing import Union
from icecream import ic
from domain.entities.unknown_user import UnknownUser


class UserChatMailingService:
    def __init__(self, repository_provider: RepositoriesDependencyProvider):
        self._companies_repository = repository_provider.get_companies_repository()
        self._user_chat_repository = repository_provider.get_user_chats_repository()
    
    async def get_company_keyboard(self, user_id: int):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        companies_codes = await self._companies_repository.get_companies_codes_by_user_id(user_id)
        for company_code in companies_codes:
            text = await self._companies_repository.get_name_by_company_code(company_code[0])
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton(text=text,
                                    callback_data=f"user_go_to mail_menu_company_code:{company_code[0]}")]
            )
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")])
        return keyboard
    
    def get_mailing_menu(self):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Создать сообщение", callback_data="user_go_to mail_create_message")])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="Почтовый ящик", callback_data="user_go_to mail_inbox")])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")])

        return keyboard
        
        
        