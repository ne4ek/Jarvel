from application.providers.repositories_provider import RepositoriesDependencyProvider
from domain.entities.task import Task
from .send_task_notification_service import SendTaskNotificationService
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


class UserChatTaskService:
    def __init__(self, repository_provider: RepositoriesDependencyProvider, task_notification_service: SendTaskNotificationService):
        self.task_repository = repository_provider.get_tasks_repository()
        self.task_notification_service = task_notification_service
    
    async def task_accepted(self, task_id: int):
        task: Task = await self.task_repository.get_by_task_id(task_id)
        await self.task_repository.set_status(task_id, "active")
        await self.task_notification_service.send_order_is_accepted(task)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В задачу", callback_data=f"user_go_to task_id:{task_id}")]])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")])
        text = "Задача принята!\nЗаказчик будет уведомлен об этом."
        return {"text": text, "keyboard": keyboard}
    
    async def get_personal_task_from_notification(self, task_id: int):
        task: Task = self.task_repository.get_by_task_id(task_id)
        if task.status == "active":
            change_status_button = InlineKeyboardButton(text="Завершить задачу", callback_data=f"mark_task_complete:{task_id}")
    