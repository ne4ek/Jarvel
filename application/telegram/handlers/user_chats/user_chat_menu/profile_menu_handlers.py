from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from application.profile_menu.services.profile_menu_service import ProfileMenuService
from application.telegram.models.state_forms import PersonalInfoChange
from icecream import ic

class ProfileMenuHandlers:
    def __init__(self, profile_menu_service: ProfileMenuService):
        self.profile_menu_service = profile_menu_service
    
    def get_router(self):
        router = Router()
        self.__register_callbacks(router)
        self.__register_states(router)
        return router
    
    def __register_callbacks(self, router: Router):
        router.callback_query.register(self.profile_menu_start_callback, F.data == "user_go_to profile_menu")
        router.callback_query.register(self.change_name_callback, F.data == "user_go_to change_name")
        router.callback_query.register(self.confirm_name_change_callback, F.data == "user_change_name confirm")
        router.callback_query.register(self.change_email_callback, F.data == "user_go_to change_email")
        router.callback_query.register(self.confirm_email_change_callback, F.data == "user_change_email confirm")
        router.callback_query.register(self.get_company_menu_callback, F.data == "user_go_to my_companies") 
    
    def __register_states(self, router: Router):
        router.message(PersonalInfoChange.choosing_firstname, F.chat.type == "private")(self.change_name_state)
        router.message(PersonalInfoChange.choosing_lastname, F.chat.type == "private")(self.change_last_name_state)
        router.message(PersonalInfoChange.choosing_email, F.chat.type == "private")(self.change_email_state)
    
    async def profile_menu_start_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        response = await self.profile_menu_service.profile_menu_start(callback.from_user.id)
        await callback.message.edit_text(text=response["text"], reply_markup=response["keyboard"])

    
    async def change_name_callback(self, callback: types.CallbackQuery, state: FSMContext):
        response = self.profile_menu_service.profile_menu_change_name()
        await state.set_state(PersonalInfoChange.choosing_firstname)
        await state.update_data({"bot_message": callback.message})
        await callback.message.edit_text(text=response["text"], reply_markup=response["keyboard"])
    
    async def change_name_state(self, message: types.Message, state: FSMContext):
        firts_name = message.text.capitalize()
        await state.update_data(first_name=firts_name)
        data = await state.get_data()
        if data.get("last_name"):
            await state.set_state(PersonalInfoChange.empty)
            response = self.profile_menu_service.profile_menu_get_change_name_confirmation(firts_name, data.get("last_name"))
        else:
            await state.set_state(PersonalInfoChange.choosing_lastname)
            response = self.profile_menu_service.profile_menu_change_lastname()
            data = await state.get_data()
        bot_message = data.get("bot_message")
        await message.delete()
        await bot_message.edit_text(text=response["text"], reply_markup=response["keyboard"])

    async def change_last_name_state(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        last_name = message.text.capitalize()
        first_name = data.get("first_name")
        await state.update_data(last_name=last_name)
        await state.set_state(PersonalInfoChange.empty)
        response = self.profile_menu_service.profile_menu_get_change_name_confirmation(first_name, last_name)
        bot_message = data.get("bot_message")
        await message.delete()
        await bot_message.edit_text(text=response["text"], reply_markup=response["keyboard"])
    
    async def confirm_name_change_callback(self, callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        response = await self.profile_menu_service.update_name(callback.from_user.id, first_name, last_name)
        await state.clear()
        await callback.message.edit_text(text=response["text"], reply_markup=response["keyboard"])
    
    async def change_email_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await state.set_state(PersonalInfoChange.choosing_email)
        await state.update_data({"bot_message": callback.message})
        response = self.profile_menu_service.profile_menu_change_email()
        await callback.message.edit_text(text=response["text"], reply_markup=response["keyboard"])
    
    async def change_email_state(self, message: types.Message, state: FSMContext):
        response = await self.profile_menu_service.profile_menu_get_change_email_confirmation(state, message.text)
        data = await state.get_data()
        bot_message = data.get("bot_message")
        await message.delete()
        await bot_message.edit_text(text=response["text"], reply_markup=response["keyboard"])
    
    async def confirm_email_change_callback(self, callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        new_email = data.get("new_email")
        response = await self.profile_menu_service.update_email(callback.from_user.id, new_email)
        await state.clear()
        await callback.message.edit_text(text=response["text"], reply_markup=response["keyboard"])
    
    async def get_company_menu_callback(self, callback: types.CallbackQuery, state: FSMContext):
        ic("user companies")
        user_id = callback.from_user.id
        response = await self.profile_menu_service.profile_menu_my_companies(user_id)
        await callback.message.edit_text(text=response["text"], reply_markup=response["keyboard"], parse_mode="HTML")