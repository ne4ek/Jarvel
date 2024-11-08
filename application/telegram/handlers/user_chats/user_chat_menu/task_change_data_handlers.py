from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from application.tasks.services.edit_task_data_service import EditTaskDataService
from application.tasks.services.user_chat_task_menu_service import TaskMenuService
from application.telegram.models.state_forms import PersonalTaskChange, AuthorTaskChange
from application.messages.message_transcriber import audio_to_text_converter
from icecream import ic

class UserChatEditTaskHandlers:
    def __init__(self, edit_task_data_service: EditTaskDataService, task_menu_service: TaskMenuService) -> None:
        self.task_edit_data_service = edit_task_data_service
        self.task_menu_service = task_menu_service
    
    def get_router(self):
        router = Router()
        self.__register_states(router)
        self.__register_callbacks(router)
        return router
    
    def __register_callbacks(self, router: Router):
        router.callback_query.register(self.edit_p_task_description_callback, F.data.startswith("p_task_change description"))
        router.callback_query.register(self.edit_p_task_tag_callback, F.data.startswith("p_task_change tag"))
        router.callback_query.register(self.edit_p_task_deadline_callback, F.data.startswith("p_task_change deadline"))
        router.callback_query.register(self.edit_order_description_callback, F.data.startswith("order_change description"))
        router.callback_query.register(self.edit_order_tag_callback, F.data.startswith("order_change tag"))
        router.callback_query.register(self.edit_order_deadline_callback, F.data.startswith("order_change deadline"))
    
    def __register_states(self, router: Router):
        router.message(PersonalTaskChange.user_changing_data, F.chat.type == "private")(self.edit_p_task_data_state)
        router.message(AuthorTaskChange.author_changing_data, F.chat.type == "private")(self.edit_order_data_state)
    
    async def edit_p_task_description_callback(self, callback: types.CallbackQuery, state: FSMContext):
        task_id = int(callback.data.split(":")[-1])
        text = callback.message.text + "\n\nУкажите новое описание"
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="К задаче", callback_data=f"user_go_to p_task_id:{task_id}")]])
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        await state.set_state(PersonalTaskChange.user_changing_data)
        await state.update_data({"p_task_id": task_id, "p_task_bot_message": callback.message, "p_task_data_to_edit": "description"})
    
    async def edit_p_task_deadline_callback(self, callback: types.CallbackQuery, state: FSMContext):
        task_id = int(callback.data.split(":")[-1])
        text = callback.message.text + "\n\nУкажите новый дедлайн"
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="К задаче", callback_data=f"user_go_to p_task_id:{task_id}")]])
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        await state.set_state(PersonalTaskChange.user_changing_data)
        await state.update_data({"p_task_id": task_id, "p_task_bot_message": callback.message, "p_task_data_to_edit": "deadline"})
    
    async def edit_p_task_tag_callback(self, callback: types.CallbackQuery, state: FSMContext):
        task_id = int(callback.data.split(":")[-1])
        text = callback.message.text + "\n\nУкажите новый тег"
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="К задаче", callback_data=f"user_go_to p_task_id:{task_id}")]])
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        await state.set_state(PersonalTaskChange.user_changing_data)
        await state.update_data({"p_task_id": task_id, "p_task_bot_message": callback.message, "p_task_data_to_edit": "tag"})
    
    @audio_to_text_converter
    async def edit_p_task_data_state(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        task_id = data.get("p_task_id")
        bot_message = data.get("p_task_bot_message")
        data_to_edit = data.get("p_task_data_to_edit")
        if data_to_edit == "description":
            await self.task_edit_data_service.change_task_description(message, task_id)
        elif data_to_edit == "deadline":
            await self.task_edit_data_service.change_task_deadline(message, task_id)
        elif data_to_edit == "tag":
            await self.task_edit_data_service.change_task_tag(message, task_id)
        response = await self.task_menu_service.get_personal_task_menu(p_task_id=task_id)
        text = response.get("text")
        keyboard = response.get("keyboard")
        await state.clear()
        await bot_message.edit_text(text=text, reply_markup=keyboard)
        await message.delete()
    
    async def edit_order_description_callback(self, callback: types.CallbackQuery, state: FSMContext):
        task_id = int(callback.data.split(":")[-1])
        text = callback.message.text + "\n\nУкажите новое описание"
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="К заказу", callback_data=f"user_go_to order_id:{task_id}")]])
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        await state.set_state(AuthorTaskChange.author_changing_data)
        await state.update_data({"order_id": task_id, "order_bot_message": callback.message, "order_data_to_edit": "description"})
    
    async def edit_order_deadline_callback(self, callback: types.CallbackQuery, state: FSMContext):
        task_id = int(callback.data.split(":")[-1])
        text = callback.message.text + "\n\nУкажите новый дедлайн"
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="К задаче", callback_data=f"user_go_to order_id:{task_id}")]])
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        await state.set_state(AuthorTaskChange.author_changing_data)
        await state.update_data({"order_id": task_id, "order_bot_message": callback.message, "order_data_to_edit": "deadline"})
    
    async def edit_order_tag_callback(self, callback: types.CallbackQuery, state: FSMContext):
        task_id = int(callback.data.split(":")[-1])
        text = callback.message.text + "\n\nУкажите новый тег"
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="К задаче", callback_data=f"user_go_to order_id:{task_id}")]])
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        await state.set_state(AuthorTaskChange.author_changing_data)
        await state.update_data({"order_id": task_id, "order_bot_message": callback.message, "order_data_to_edit": "tag"})
    
    @audio_to_text_converter
    async def edit_order_data_state(self, message: types.Message, state: FSMContext):
        data = await state.get_data()
        task_id = data.get("order_id")
        bot_message = data.get("order_bot_message")
        data_to_edit = data.get("order_data_to_edit")
        if data_to_edit == "description":
            await self.task_edit_data_service.change_task_description(message, task_id)
        elif data_to_edit == "deadline":
            await self.task_edit_data_service.change_task_deadline(message, task_id)
        elif data_to_edit == "tag":
            await self.task_edit_data_service.change_task_tag(message, task_id)
        response = await self.task_menu_service.get_order_menu(order_id=task_id)
        text = response.get("text")
        keyboard = response.get("keyboard")
        await state.clear()
        await bot_message.edit_text(text=text, reply_markup=keyboard)
        await message.delete()