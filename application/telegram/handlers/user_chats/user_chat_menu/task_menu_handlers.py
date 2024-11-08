from aiogram import types, Router, F
from aiogram.fsm.context import FSMContext
from application.tasks.services.user_chat_task_menu_service import TaskMenuService
from icecream import ic

class TaskMenuHandlers:
    def __init__(self, task_menu_service: TaskMenuService) -> None:
        self.task_menu_service = task_menu_service
    
    def get_router(self):
        router = Router()
        self.register_callbacks(router)
        return router
    
    def register_callbacks(self, router: Router):
        router.callback_query.register(self.task_menu_start_callback, F.data=="user_go_to tasks_choose_company")
        router.callback_query.register(self.choose_company_callback, F.data.startswith("user_go_to choose_task_type"))
        router.callback_query.register(self.task_list_callback, F.data.startswith("user_go_to menu_tasks"))
        router.callback_query.register(self.order_list_callback, F.data.startswith("user_go_to menu_orders"))
        router.callback_query.register(self.personal_task_list_callback, F.data.startswith("user_go_to p_tasks"))
        router.callback_query.register(self.task_menu_callback, F.data.startswith("user_go_to task_id"))
        router.callback_query.register(self.order_menu_callback, F.data.startswith("user_go_to order_id"))
        router.callback_query.register(self.personal_task_menu_callback, F.data.startswith("user_go_to p_task_id"))
        router.callback_query.register(self.mark_task_complete_callback, F.data.startswith("task_set_complete"))
        router.callback_query.register(self.mark_task_active_callback, F.data.startswith("task_set_active"))
        router.callback_query.register(self.mark_order_cancelled_callback, F.data.startswith("order_set_cancelled"))
        router.callback_query.register(self.archive_task_type_callback, F.data.startswith("user_go_to menu_task_archive"))
        router.callback_query.register(self.archive_task_list_callback, F.data.startswith("user_go_to archive_tasks"))
        router.callback_query.register(self.archive_order_list_callback, F.data.startswith("user_go_to archive_orders"))
        router.callback_query.register(self.archive_personal_task_list_callback, F.data.startswith("user_go_to archive_p_tasks"))
        router.callback_query.register(self.mark_order_pending_callback, F.data.startswith("order_set_pending"))
        router.callback_query.register(self.mark_personal_task_active, F.data.startswith("p_task_set_active"))
        router.callback_query.register(self.mark_personal_task_complete, F.data.startswith("p_task_set_complete"))
    
    def register_handlers(self, router: Router):
        pass
    
    async def task_menu_start_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        text = "Выберите компанию:"
        keyboard = await self.task_menu_service.get_company_keyboard(callback.from_user.id)
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def choose_company_callback(self, callback: types.CallbackQuery, state: FSMContext):
        text = "Выберите тип задач:"
        keyboard = self.task_menu_service.get_task_type_keyboard(company_code=callback.data.split(":")[-1])
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def task_list_callback(self, callback: types.CallbackQuery, state: FSMContext):
        
        response = await self.task_menu_service.get_task_list(callback.from_user.id, company_code=callback.data.split(":")[-1])
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def order_list_callback(self, callback: types.CallbackQuery, state: FSMContext):
        response = await self.task_menu_service.get_order_list(callback.from_user.id, company_code=callback.data.split(":")[-1])
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def personal_task_list_callback(self, callback: types.CallbackQuery):
        response = await self.task_menu_service.get_personal_task_list(callback.from_user.id, company_code=callback.data.split(":")[-1])
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def archive_task_type_callback(self, callback: types.CallbackQuery):
        response = self.task_menu_service.get_archive_task_type_keyboard(company_code=callback.data.split(":")[-1])
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def archive_task_list_callback(self, callback: types.CallbackQuery):
        response = await self.task_menu_service.get_archive_task_list(callback.from_user.id, company_code=callback.data.split(":")[-1])
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def archive_order_list_callback(self, callback: types.CallbackQuery):
        response = await self.task_menu_service.get_archive_order_list(callback.from_user.id, company_code=callback.data.split(":")[-1])
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def archive_personal_task_list_callback(self, callback: types.CallbackQuery):
        response = await self.task_menu_service.get_archive_personal_task_list(callback.from_user.id, company_code=callback.data.split(":")[-1])
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def task_menu_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        response = await self.task_menu_service.get_task_menu(task_id=int(callback.data.split(":")[-1]))

        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def order_menu_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        back_to_list_button = callback.message.reply_markup.inline_keyboard[-1][0]
        response = await self.task_menu_service.get_order_menu(order_id=int(callback.data.split(":")[-1]))
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def mark_task_complete_callback(self, callback: types.CallbackQuery):
        response = await self.task_menu_service.mark_task_complete(task_id=int(callback.data.split(":")[-1]))
        bot = callback.bot
        
        text = response.get("text")
        keyboard = response.get("keyboard")
        author_text = response.get("author_text")
        author_id = response.get("author_id")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        
        if author_text:
            await bot.send_message(chat_id=author_id, text=author_text)

    async def mark_task_active_callback(self, callback: types.CallbackQuery):
        response = await self.task_menu_service.mark_task_active(task_id=int(callback.data.split(":")[-1]))
        bot = callback.bot
        
        text = response.get("text")
        keyboard = response.get("keyboard")
        author_text = response.get("author_text")
        author_id = response.get("author_id")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        
        if author_text:
            await bot.send_message(chat_id=author_id, text=author_text)

    async def mark_order_cancelled_callback(self, callback: types.CallbackQuery):
        response = await self.task_menu_service.mark_order_cancelled(order_id=int(callback.data.split(":")[-1]))
        bot = callback.bot
        
        text = response.get("text")
        keyboard = response.get("keyboard")
        executor_text = response.get("executor_text")
        executor_id = response.get("executor_id")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        
        if executor_text:
            await bot.send_message(chat_id=executor_id, text=executor_text)
    
    async def mark_order_pending_callback(self, callback: types.CallbackQuery):
        response = await self.task_menu_service.mark_order_pending(order_id=int(callback.data.split(":")[-1]))
        bot = callback.bot
        
        text = response.get("author_text")
        keyboard = response.get("author_keyboard")
        executor_text = response.get("executor_text")
        executor_id = response.get("executor_id")
        executor_keyboard = response.get("executor_keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
        
        if executor_text:
            await bot.send_message(chat_id=executor_id, text=executor_text, reply_markup=executor_keyboard)
    
    async def personal_task_menu_callback(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        response = await self.task_menu_service.get_personal_task_menu(p_task_id=int(callback.data.split(":")[-1]))
        # ic(response)
        text = response.get("text") 
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def mark_personal_task_complete(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        response = await self.task_menu_service.mark_personal_task_complete(p_task_id=int(callback.data.split(":")[-1]))
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)
    
    async def mark_personal_task_active(self, callback: types.CallbackQuery, state: FSMContext):
        await state.clear()
        response = await self.task_menu_service.mark_personal_task_active(p_task_id=int(callback.data.split(":")[-1]))
        text = response.get("text")
        keyboard = response.get("keyboard")
        await callback.message.edit_text(text=text, reply_markup=keyboard)