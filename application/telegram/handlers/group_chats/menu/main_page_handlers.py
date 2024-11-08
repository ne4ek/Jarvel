from application.telegram.group_chat_menu.services.main_page_service import MainPageService
from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode
from application.telegram.decorators import group_chat_callback_decorator

class GroupMenuMainPageHandlers:
    def __init__(self, menu_service: MainPageService):
        self.menu_service = menu_service
        
    def get_router(self):
        router = Router()
        self.__register_callbacks(router)
        self.__register_command(router)
        return router
    
    def __register_callbacks(self, router: Router) -> None:
        router.callback_query.register(self.task_button_callback_handler, F.data == "group_go_to task_filling_main")
        router.callback_query.register(self.meeting_button_callback_handler, F.data == "group_go_to meeting_filling_main")
        router.callback_query.register(self.mailing_button_callback_handler, F.data == "group_go_to mail_filling_main")
        router.callback_query.register(self.info_button_callback_handler, F.data == "group_go_to chat_info")
        router.callback_query.register(self.edit_chat_button_callback_handler, F.data == "group_go_to edit_chat_menu")
        router.callback_query.register(self.main_menu_button_callback_handler, F.data == "group_go_to main_menu")
        router.callback_query.register(self.delete_chat_from_company_handler, F.data == "group_delete_company_from_chat")
    
    def __register_command(self, router: Router) -> None:
        router.message(Command("main_menu"), F.chat.type != "private")(self.main_menu_command_handler)
    
    async def main_menu_command_handler(self, message: types.Message, state: FSMContext):
        await state.clear()
        response = self.menu_service.get_menu_main_page()
        text = response.get("text")
        keyboard = response.get("keyboard")
        await message.reply(text=text, reply_markup=keyboard)
    
    @group_chat_callback_decorator
    async def main_menu_button_callback_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        response = self.menu_service.get_menu_main_page()
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    @group_chat_callback_decorator    
    async def task_button_callback_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        response = await self.menu_service.get_task_filling_menu(state, callback.message, callback.from_user.id)
        text = response.get("message")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    @group_chat_callback_decorator
    async def meeting_button_callback_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        response = await self.menu_service.get_meeting_filling_menu(state, callback.message, callback.from_user.id)
        text = response.get("message")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    @group_chat_callback_decorator
    async def mailing_button_callback_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        response = await self.menu_service.get_mailing_filling_menu(state, callback.message, callback.from_user.id)
        text = response.get("message")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    @group_chat_callback_decorator
    async def info_button_callback_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        response = await self.menu_service.get_info_menu(callback.message.chat.id)
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard, parse_mode=ParseMode.HTML)
    
    @group_chat_callback_decorator
    async def edit_chat_button_callback_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        response = await self.menu_service.get_edit_chat_menu(callback.message.chat.id)
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    @group_chat_callback_decorator
    async def delete_chat_from_company_handler(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        response = await self.menu_service.delete_company_from_chat(callback.message.chat.id)
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)