from aiogram import Dispatcher, F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from application.notification.services.notification_service import NotificationService


class CreateNotificationHandler:
    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def register_all_meetings_handlers_and_callbacks(self, dp: Dispatcher):
        self.register_callback(dp)
        router = Router()
        return self.register_handlers(router)

    def register_handlers(self, router: Router):
        return router

    def register_callback(self, dp: Dispatcher):
        pass

    # async def start_notification_handler(self, args):
