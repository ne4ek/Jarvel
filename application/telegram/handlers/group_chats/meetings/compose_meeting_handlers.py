from application.meetings.services.telegram_compose_meeting_service import TelegramComposeMeetingService
from .keyboards.compose_meeting_keyboard import get_change_invitation_type_keyboard, get_go_to_menu_meetings_filling, get_go_to_main_menu_keyboard
from application.telegram.models.state_forms import MeetingState
from application.messages.message_transcriber import audio_to_text_converter
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from icecream import ic
from application.telegram.decorators import group_chat_callback_decorator

class ComposeMeetingHandlers:
    def __init__(self, compose_meeting_service: TelegramComposeMeetingService):
        self.compose_meeting_service = compose_meeting_service

    def get_router(self) -> Router:
        router = Router()
        self.__register_callbacks(router)
        self.__register_handlers(router)
        return router
    
    def __register_handlers(self, router: Router) -> None:
        router.message(MeetingState.change_topic, F.chat.type != "private")(self.clarify_meeting_topic_state)
        router.message(MeetingState.change_meeting_time, F.chat.type != "private")(self.clarify_meeting_time_state)
        router.message(MeetingState.change_remind_time, F.chat.type != "private")(self.clarify_meeting_remind_time_state)
        router.message(MeetingState.change_moderator, F.chat.type != "private")(self.clarify_meeting_moderator_state)
        router.message(MeetingState.change_participants, F.chat.type != "private")(self.clarify_meeting_participants_state)
        router.message(MeetingState.change_link, F.chat.type != "private")(self.clarify_meeting_link_state)
        router.message(MeetingState.change_duration, F.chat.type != "private")(self.clarify_meeting_duration_state)
    
    def __register_callbacks(self, router: Router) -> None:
        router.callback_query.register(self.clarify_meeting_topic_callback, F.data == "meeting_filling_change topic")
        router.callback_query.register(self.clarify_meeting_time_callback, F.data == "meeting_filling_change meeting_time")
        router.callback_query.register(self.clarify_meeting_remind_time_callback, F.data == "meeting_filling_change remind_time")
        router.callback_query.register(self.clarify_meeting_moderator_callback, F.data == "meeting_filling_change moderator")
        router.callback_query.register(self.clarify_meeting_participants_callback, F.data == "meeting_filling_change participants")
        router.callback_query.register(self.clarify_meeting_link_callback, F.data == "meeting_filling_change link")
        router.callback_query.register(self.clarify_meeting_invitation_type_callback, F.data == "meeting_filling_change invitation_type")
        router.callback_query.register(self.clarify_meeting_duration_callback, F.data == "meeting_filling_change duration")
        router.callback_query.register(self.delete_meeting_callback, F.data == "meeting_filling_delete")
        router.callback_query.register(self.go_back_to_filling_callback, F.data == "meeting_filling back")
        router.callback_query.register(self.save_meeting_callback, F.data == "meeting_save")
        router.callback_query.register(self.set_meeting_invtation_type_callback, F.data.startswith("meeting_filling_change invitation_type"))
    
    @group_chat_callback_decorator
    async def clarify_meeting_topic_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nУкажите тему встречи"
        await callback.message.edit_text(text=bot_message_text, reply_markup=get_go_to_menu_meetings_filling())
        await state.set_state(MeetingState.change_topic)
    
    @group_chat_callback_decorator
    async def clarify_meeting_time_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nУкажите время встречи"
        await callback.message.edit_text(text=bot_message_text, reply_markup=get_go_to_menu_meetings_filling())
        await state.set_state(MeetingState.change_meeting_time)
    
    @group_chat_callback_decorator
    async def clarify_meeting_remind_time_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nУкажите время напоминания о встрече"
        await callback.message.edit_text(text=bot_message_text, reply_markup=get_go_to_menu_meetings_filling())
        await state.set_state(MeetingState.change_remind_time)
    
    @group_chat_callback_decorator
    async def clarify_meeting_moderator_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nУкажите модератора встречи"
        await callback.message.edit_text(text=bot_message_text, reply_markup=get_go_to_menu_meetings_filling())
        await state.set_state(MeetingState.change_moderator)
    
    @group_chat_callback_decorator
    async def clarify_meeting_participants_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nУкажите участников встречи"
        await callback.message.edit_text(text=bot_message_text, reply_markup=get_go_to_menu_meetings_filling())
        await state.set_state(MeetingState.change_participants)
    
    @group_chat_callback_decorator
    async def clarify_meeting_link_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nУкажите ссылку на встречу"
        await callback.message.edit_text(text=bot_message_text, reply_markup=get_go_to_menu_meetings_filling())
        await state.set_state(MeetingState.change_link)
    
    @group_chat_callback_decorator
    async def clarify_meeting_invitation_type_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n Укажите тип приглашения"
        await callback.message.edit_text(text=bot_message_text, reply_markup=get_change_invitation_type_keyboard())
        await state.set_state(MeetingState.change_invitation_type)
    
    @group_chat_callback_decorator  
    async def set_meeting_invtation_type_callback(self, callback: types.CallbackQuery, state: FSMContext):
        data = await state.get_data()
        meeting = data.get("meeting").get("entity")
        meeting.invitation_type = callback.data.split(":")[1]
        await state.update_data({"meeting": {"entity": meeting, "message": callback.message}})
        response = await self.compose_meeting_service.get_telegram_message(state)
        text = response.get("message")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        await state.set_state(MeetingState.empty)
    
    @group_chat_callback_decorator   
    async def clarify_meeting_duration_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nУкажите продолжительность встречи"
        await callback.message.edit_text(text=bot_message_text, reply_markup=get_go_to_menu_meetings_filling())
        await state.set_state(MeetingState.change_duration)
    
    @group_chat_callback_decorator
    async def delete_meeting_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(text="Встреча удалена", reply_markup=get_go_to_main_menu_keyboard())
        await state.clear()
    
    @group_chat_callback_decorator
    async def go_back_to_filling_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message = await self.compose_meeting_service.get_telegram_message(state)
        await state.set_state(MeetingState.empty)
        await callback.message.edit_text(text=bot_message.get("message"), reply_markup=bot_message.get("keyboard"))

    @group_chat_callback_decorator
    async def save_meeting_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text(text="Встреча сохранена!\nУчастники встречи и модератор получат оповещение о встрече", reply_markup=get_go_to_main_menu_keyboard())
        await self.compose_meeting_service.save_meeting(state)
        await state.clear()
        
    @audio_to_text_converter
    async def clarify_meeting_topic_state(self, message: types.Message, state: FSMContext):
        response = await self.compose_meeting_service.change_meeting_topic(message, state)
        data = await state.get_data()
        meeting_message_data = data.get("meeting")
        ic(meeting_message_data.keys())
        bot_message: types.Message = meeting_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MeetingState.empty)
    
    @audio_to_text_converter
    async def clarify_meeting_time_state(self, message: types.Message, state: FSMContext):
        response = await self.compose_meeting_service.change_meeting_datetime(message, state)
        data = await state.get_data()
        meeting_message_data = data.get("meeting")
        bot_message: types.Message = meeting_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MeetingState.empty)
    
    @audio_to_text_converter
    async def clarify_meeting_remind_time_state(self, message: types.Message, state: FSMContext):
        response = await self.compose_meeting_service.change_meeting_remind_time(message, state)
        data = await state.get_data()
        meeting_message_data = data.get("meeting")
        bot_message: types.Message = meeting_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MeetingState.empty)
    
    @audio_to_text_converter
    async def clarify_meeting_moderator_state(self, message: types.Message, state: FSMContext):
        response = await self.compose_meeting_service.change_meeting_moderator(message, state)
        data = await state.get_data()
        meeting_message_data = data.get("meeting")
        bot_message: types.Message = meeting_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MeetingState.empty)
    
    @audio_to_text_converter
    async def clarify_meeting_participants_state(self, message: types.Message, state: FSMContext):
        response = await self.compose_meeting_service.change_meeting_participants(message, state)
        data = await state.get_data()
        meeting_message_data = data.get("meeting")
        bot_message: types.Message = meeting_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MeetingState.empty)
    
    @audio_to_text_converter
    async def clarify_meeting_duration_state(self, message: types.Message, state: FSMContext):
        response = await self.compose_meeting_service.change_meeting_duration(message, state)
        data = await state.get_data()
        meeting_message_data = data.get("meeting")
        bot_message: types.Message = meeting_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MeetingState.empty)


    async def clarify_meeting_link_state(self, message: types.Message, state: FSMContext):
        response = await self.compose_meeting_service.change_meeting_link(message, state)
        data = await state.get_data()
        meeting_message_data = data.get("meeting")
        bot_message: types.Message = meeting_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(MeetingState.empty)