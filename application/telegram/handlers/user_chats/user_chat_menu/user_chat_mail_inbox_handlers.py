from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from application.mailing.services.user_chat_mail_inbox_service import UserChatInboxService


class UserChatMailInboxHandlers:
    def __init__(self, mailing_service: UserChatInboxService):
        self._mailing_service = mailing_service

    def get_router(self):
        router = Router()
        self._register_callbacks(router)
        return router

    def _register_callbacks(self, router: Router):
        router.callback_query.register(self.inbox_start_callback, F.data == "user_go_to mail_inbox")
    
    async def inbox_start_callback(self, callback: types.CallbackQuery, state: FSMContext):
        response = await self._mailing_service.get_mail_inbox_menu(state)
        await callback.message.edit_text(text=response.get("text"),
                                         reply_markup=response.get("keyboard"))
        