from application.tasks.services.telegram_compose_task_service import TelegramComposeTaskService
from application.telegram.handlers.group_chats.tasks.keyboards.compose_task_keyboard import get_go_to_filling_keyboard, get_go_to_main_menu_keyboard
from application.telegram.models.state_forms import TaskState
from application.messages.message_transcriber import audio_to_text_converter
from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from icecream import ic
from application.telegram.decorators import group_chat_callback_decorator

class ComposeTaskHandlers:
    def __init__(self, task_service: TelegramComposeTaskService):
        self.task_service = task_service

    def get_router(self):
        router = Router()
        self.__register_callbacks(router)
        self.__register_handlers(router)
        return router

    def __register_handlers(self, router: Router) -> None:
        router.message(TaskState.change_author, F.chat.type != "private")(self.change_task_author_state)
        router.message(TaskState.change_executor, F.chat.type != "private")(self.change_task_executor_state)
        router.message(TaskState.change_deadline, F.chat.type != "private")(self.change_task_deadline_state)
        router.message(TaskState.change_decription, F.chat.type != "private")(self.change_task_description_state)
        router.message(TaskState.change_tag, F.chat.type != "private")(self.change_task_tag_state)

    def __register_callbacks(self, router: Router) -> None:
        router.callback_query.register(self.change_task_author_callback, F.data == "task_filling_change author")
        router.callback_query.register(self.change_task_executor_callback, F.data == "task_filling_change executor")
        router.callback_query.register(self.change_task_deadline_callback, F.data == "task_filling_change deadline")
        router.callback_query.register(self.change_task_description_callback, F.data == "task_filling_change description")
        router.callback_query.register(self.change_task_tag_callback, F.data == "task_filling_change tag")
        router.callback_query.register(self.go_back_to_filling_callback, F.data == "task_filling back")
        router.callback_query.register(self.delete_task_callback, F.data == "task_filling_delete")
        router.callback_query.register(self.save_task_callback, F.data == "task_save")
    
    @group_chat_callback_decorator
    async def change_task_author_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nВведите автора задачи"
        await callback.message.edit_text(bot_message_text, reply_markup=get_go_to_filling_keyboard())
        await state.set_state(TaskState.change_author)
    
    @group_chat_callback_decorator
    async def change_task_executor_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nВведите исполнителя задачи"
        await callback.message.edit_text(bot_message_text, reply_markup=get_go_to_filling_keyboard())
        await state.set_state(TaskState.change_executor)
    
    @group_chat_callback_decorator
    async def change_task_deadline_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nВведите дедлайн задачи"
        await callback.message.edit_text(bot_message_text, reply_markup=get_go_to_filling_keyboard())
        await state.set_state(TaskState.change_deadline)
    
    @group_chat_callback_decorator
    async def change_task_description_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nВведите описание задачи"
        await callback.message.edit_text(bot_message_text, reply_markup=get_go_to_filling_keyboard())
        await state.set_state(TaskState.change_decription)
    
    @group_chat_callback_decorator
    async def change_task_tag_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message_text = callback.message.text
        bot_message_text += "\n\nВведите тэг задачи"
        await callback.message.edit_text(bot_message_text, reply_markup=get_go_to_filling_keyboard())
        await state.set_state(TaskState.change_tag)
    
    @group_chat_callback_decorator
    async def delete_task_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await callback.message.edit_text("Задача удалена", reply_markup=get_go_to_main_menu_keyboard())
        await state.clear()
    
    @group_chat_callback_decorator
    async def save_task_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await self.task_service.save_task(state)
        await callback.message.edit_text("Задача успешно отправлена исполнителю!", reply_markup=get_go_to_main_menu_keyboard())
        await state.clear()
    
    @group_chat_callback_decorator
    async def go_back_to_filling_callback(self, callback: types.CallbackQuery, state: FSMContext):
        bot_message = await self.task_service.get_telegram_message(state)
        await state.set_state(TaskState.empty)
        await callback.message.edit_text(text=bot_message.get("message"), reply_markup=bot_message.get("keyboard"))
    
    @audio_to_text_converter
    async def change_task_author_state(self, message: types.Message, state: FSMContext):
        response = await self.task_service.change_task_author(message, state)
        # ic(response)
        data = await state.get_data()
        task_message_data = data.get("task")
        bot_message: types.Message = task_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(TaskState.empty)
    
    @audio_to_text_converter
    async def change_task_executor_state(self, message: types.Message, state: FSMContext):
        response = await self.task_service.change_task_executor(message, state)
        data = await state.get_data()
        task_message_data = data.get("task")
        bot_message: types.Message = task_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(TaskState.empty)
    
    @audio_to_text_converter
    async def change_task_deadline_state(self, message: types.Message, state: FSMContext):
        response = await self.task_service.change_task_deadline(message, state)
        data = await state.get_data()
        task_message_data = data.get("task")
        bot_message: types.Message = task_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(TaskState.empty)
    
    @audio_to_text_converter
    async def change_task_description_state(self, message: types.Message, state: FSMContext):
        response = await self.task_service.change_task_description(message, state)
        data = await state.get_data()
        task_message_data = data.get("task")
        bot_message: types.Message = task_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(TaskState.empty)
    
    @audio_to_text_converter
    async def change_task_tag_state(self, message: types.Message, state: FSMContext):
        response = await self.task_service.change_task_tag(message, state)
        data = await state.get_data()
        task_message_data = data.get("task")
        bot_message: types.Message = task_message_data.get("message")
        await message.delete()
        await bot_message.edit_text(text=response.get("message"), reply_markup=response.get("keyboard"))
        await state.set_state(TaskState.empty)
