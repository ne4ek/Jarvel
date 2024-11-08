from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from .keyboards.main_menu_keyboard import get_main_menu_keyboard


class MainMenuHandlers:
    def __init__(self):
        pass
    
    def get_router(self):
        router = Router()
        router.callback_query.register(self.main_menu_callback, F.data == "user_go_to main_menu")
        return router
    
    async def __call__(self, message: types.Message, state: FSMContext):
        await state.clear()
        text = "Выберите пункт меню"
        keyboard = get_main_menu_keyboard()
        await message.answer(text=text, reply_markup=keyboard)
    
    async def main_menu_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        text = "Выберите пункт меню"
        keyboard = get_main_menu_keyboard()
        if callback.message.document:
            await callback.message.answer(text, reply_markup=keyboard)
            await callback.message.delete()
            callback.answer(text, reply_markup=keyboard)
        else:
            await callback.message.edit_text(text, reply_markup=keyboard)
        