from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from application.mailing.services.user_chat_mailing_service import UserChatMailingService


class UserChatMailingHandlers:
    def __init__(self, mailing_service: UserChatMailingService):
        self._mailing_service = mailing_service

    def get_router(self):
        router = Router()
        self._register_callbacks(router)
        return router

    def _register_callbacks(self, router: Router):
        router.callback_query.register(self._mailing_menu_start_callback, F.data == "user_go_to mail_choose_company")
        router.callback_query.register(self._choose_company_callback, F.data.startswith("user_go_to mail_menu_company_code:"))

    async def _mailing_menu_start_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        text = "Выберите компанию:"
        keyboard = await self._mailing_service.get_company_keyboard(callback.from_user.id)
        await callback.message.edit_text(text=text,reply_markup=keyboard)

    def __extract_company_code(self, callback_data: str):
        return callback_data.lstrip("user_go_to mail_menu_company_code:")
    
    async def _choose_company_callback(self, callback: types.CallbackQuery, state: FSMContext):
        company_code = self.__extract_company_code(callback.data)
        await state.update_data({"company_code": company_code})
        text = "Меню рассылки"
        keyboard = self._mailing_service.get_mailing_menu()
        await callback.message.edit_text(text=text, reply_markup=keyboard)

