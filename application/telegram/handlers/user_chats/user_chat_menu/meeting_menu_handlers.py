from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from application.meetings.services.meeting_menu_service import MeetingMenuService
from application.telegram.models.state_forms import MeetingMenuState
import os
from icecream import ic

class MeetingMenuHandlers:
    def __init__(self, meeting_menu_services: MeetingMenuService) -> None:
        self.meeting_menu_service = meeting_menu_services
    
    def get_router(self):
        router = Router()
        self.register_callbacks(router)
        self.register_states(router)
        return router
    
    def register_callbacks(self, router: Router):
        router.callback_query.register(self.meeting_menu_start_callback, F.data=="user_go_to meet_choose_company")
        router.callback_query.register(self.choose_company_callback, F.data.startswith("user_go_to choose_meet_filt"))
        router.callback_query.register(self.all_meeting_list_callback, F.data.startswith("user_go_to meeting_lst"))
        router.callback_query.register(self.moderator_meeting_list_callback, F.data.startswith("user_go_to meet_mod_lst"))
        router.callback_query.register(self.get_meeting_menu_callback, F.data.startswith("user_go_to meeting_id"))
        router.callback_query.register(self.get_participant_meeting_list_callback, F.data.startswith("user_go_to meet_part_lst"))
        router.callback_query.register(self.get_archive_meeting_list_callback, F.data.startswith("user_go_to meet_archive"))
        router.callback_query.register(self.moderator_set_link_callback, F.data.startswith("moderator_set_link"))
        router.callback_query.register(self.moderator_set_meeting_datetime_callback, F.data.startswith("moderator_set_datetime"))
        router.callback_query.register(self.moderator_accept_meeting_callback, F.data.startswith("meeting_moderator confirm"))
    
    def register_states(self, router: Router):
        router.message(MeetingMenuState.moderator_change_link, F.chat.type == "private")(self.moderator_set_link_state)
        router.message(MeetingMenuState.moderator_change_datetime, F.chat.type == "private")(self.moderator_set_meeting_datetime_state)
    
    async def meeting_menu_start_callback(self, callback: types.CallbackQuery):
        text = "Выберите компанию:"
        keyboard = await self.meeting_menu_service.get_company_keyboard(callback.from_user.id)
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def choose_company_callback(self, callback: types.CallbackQuery):
        text = "Выберите тип встреч:"
        keyboard = self.meeting_menu_service.get_meeting_filters_keyboard(company_code=callback.data.split(":")[-1])
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def all_meeting_list_callback(self, callback: types.CallbackQuery):
        response = await self.meeting_menu_service.get_all_meeting_list(callback.from_user.id, company_code=callback.data.split(":")[-1])
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def moderator_meeting_list_callback(self, callback: types.CallbackQuery):
        print(callback.data)
        response = await self.meeting_menu_service.get_moderator_meeting_list(callback.from_user.id, company_code=callback.data.split(":")[-1])
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def get_participant_meeting_list_callback(self, callback: types.CallbackQuery):
        print(callback.data)
        response = await self.meeting_menu_service.get_participant_meeting_list(callback.from_user.id, company_code=callback.data.split(":")[-1])
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def get_archive_meeting_list_callback(self, callback: types.CallbackQuery):
        response = await self.meeting_menu_service.archive_meeting_list(callback.from_user.id, company_code=callback.data.split(":")[-1])
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def get_meeting_menu_callback(self, callback: types.CallbackQuery, state: FSMContext):
        meeting_id = int(callback.data.split("meeting_id:")[-1])
        await state.clear()
        response = self.meeting_menu_service.get_my_meeting(callback.from_user.id, meeting_id)
        await callback.message.delete()
        bot = callback.bot
        await bot.send_document(chat_id=callback.from_user.id,
                                document=response.get("ics_file"),
                                caption=response.get("text"),
                                reply_markup=response.get("keyboard"))
        if os.path.exists(response.get("ics_file").path):
            os.remove(response.get("ics_file").path)
    
    async def moderator_accept_meeting_callback(self, callback: types.CallbackQuery):
        meeting_id = int(callback.data.split("meeting_id:")[-1])
        
        response = await self.meeting_menu_service.get_my_meeting(callback.from_user.id,
                                                            meeting_id)
        text = response.get("text")
        keyboard = response.get("keyboard")
        
        await callback.message.edit_caption(caption=text, reply_markup=keyboard)
        
    async def moderator_set_link_callback(self, callback: types.CallbackQuery, state: FSMContext):
        meeting_id = int(callback.data.split("meeting_id:")[-1])
        bot_message = callback.message
        response = self.meeting_menu_service.moderator_change_meeting_link(bot_message.caption,
                                                                           meeting_id)
        await state.set_state(MeetingMenuState.moderator_change_link)
        await state.update_data({"meeting_bot_message": bot_message, "meeting_id": meeting_id})
        await callback.message.edit_caption(caption=response.get("text"),
                                            reply_markup=response.get("keyboard"))
    
    async def moderator_set_link_state(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        bot_message: types.Message = data.get("meeting_bot_message")
        meeting_id = data.get("meeting_id")
        link = message.text
        await message.delete()
        response = await self.meeting_menu_service.update_meeting_link(message.from_user.id,
                                                                 meeting_id,
                                                                 link)
        await bot_message.delete()
        bot = message.bot
        
        await bot.send_document(chat_id=message.from_user.id,
                                document=response.get("ics_file"),
                                caption=response.get("text"),
                                reply_markup=response.get("keyboard"))
    
    async def moderator_set_meeting_datetime_callback(self, callback: types.CallbackQuery, state: FSMContext):
        meeting_id = int(callback.data.split("meeting_id:")[-1])
        bot_message = callback.message
        response = self.meeting_menu_service.moderator_change_meeting_datetime(bot_message.caption,
                                                                               meeting_id)
        await state.set_state(MeetingMenuState.moderator_change_datetime)
        await state.update_data({"meeting_bot_message": bot_message, "meeting_id": meeting_id})
        await callback.message.edit_caption(caption=response.get("text"),
                                            reply_markup=response.get("keyboard"))
    
    async def moderator_set_meeting_datetime_state(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        bot_message: types.Message = data.get("meeting_bot_message")
        meeting_id = data.get("meeting_id")
        link = message.text
        await message.delete()
        response = await self.meeting_menu_service.update_meeting_datetime(message.from_user.id,
                                                                           message.text,
                                                                           meeting_id)
        await bot_message.delete()
        bot = message.bot
        
        await bot.send_document(chat_id=message.from_user.id,
                                document=response.get("ics_file"),
                                caption=response.get("text"),
                                reply_markup=response.get("keyboard"))
    