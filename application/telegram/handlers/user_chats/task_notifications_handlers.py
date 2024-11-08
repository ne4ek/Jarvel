from aiogram import types, Router, F
from application.tasks.services.user_chat_tasks_service import UserChatTaskService

class TaskNotificationsHandlers:
    def __init__(self, task_service: UserChatTaskService):
        self.task_service = task_service
    
    def get_router(self):
        router = Router()
        self.__register_callbacks(router)
        return router
    
    def __register_callbacks(self, router: Router) -> None:
        router.callback_query.register(self.accept_task_callback, F.data.startswith("user accept_task"))
    
    async def accept_task_callback(self, callback: types.CallbackQuery):
        task_id = int(callback.data.split("task_id:")[-1])
        response = await self.task_service.task_accepted(task_id)
        await callback.message.edit_text(response.get("text"), reply_markup=response.get("keyboard"))
    
    async def go_to_personal_task_callback(self, callback: types.CallbackQuery):
        task_id = int(callback.data.split("p_task_id:")[-1])
        
        
        