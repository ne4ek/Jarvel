from application.providers.repositories_provider import RepositoriesDependencyProvider
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message
)
from domain.entities.task import Task
from datetime import datetime
from domain.contracts.assistant import Assistant
from typing import Union
from domain.entities.transcribed_message import TranscribedMessage
from .send_task_notification_service import SendTaskNotificationService
from copy import deepcopy
from icecream import ic

class EditTaskDataService:
    def __init__(self, repositories_provider: RepositoriesDependencyProvider, task_assistant: Assistant, task_notification_service: SendTaskNotificationService):
        self.task_repository = repositories_provider.get_tasks_repository()
        self.company_repository = repositories_provider.get_companies_repository()
        self.task_assistant = task_assistant
        self.user_repository = repositories_provider.get_users_repository()
        self.task_notification_service = task_notification_service
    
    async def __get_message_sender_full_name(self, user_id: int):
        return await self.user_repository.get_full_name_by_id(user_id=user_id)
    
    async def change_task_description(self, message: Union[Message, TranscribedMessage], task_id: int):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        
        old_task = await self.task_repository.get_by_task_id(task_id)
        
        task_description = old_task.task
        task_summary = old_task.task_summary
        task_tag = old_task.tag
        if task_tag in ("None", "0"):
            task_tag = None
        if task_summary in ("None", "0"):
            task_summary = None
        
        messages = [
            {"role": "system", "content": f"task: {task_description}\ntask_summary: {task_summary}\ntag: {task_tag}"},
            {"role": "system", "content": f"П ({sender_name}): {message.text}"}
        ]
        ic(old_task)
        task = deepcopy(old_task)
        new_task_description_data: dict = await self.task_assistant.change_task_description(messages)
        new_task_summary = new_task_description_data.get("task_summary")
        new_task_tag = new_task_description_data.get("tag").upper()
        new_task = new_task_description_data.get("task")
        if new_task not in ["0", None]:
            task.task = new_task
        if new_task_summary not in ["0", None]:
            task.task_summary = new_task_summary
        if new_task_tag not in ["0", None]:
            task.tag = new_task_tag
        await self.task_repository.set_description(task.task_id, new_task, new_task_summary, new_task_tag)
        if task.author_id != task.executor_id and task.status in ["pending", "active"]:
            await self.task_notification_service.send_description_changed(old_task=old_task,
                                                                          new_task=task)
        
    async def change_task_tag(self, message: Union[Message, TranscribedMessage], task_id: int):
        task = await self.task_repository.get_by_task_id(task_id)
        if message.text:
            task.tag = message.text.upper()
        await self.task_repository.set_tag(task_id, task.tag)
        
        if task.author_id != task.executor_id and task.status in ["pending", "active"]:
            await self.task_notification_service.send_tag_changed(task)
        
    async def change_task_deadline(self, message: Union[Message, TranscribedMessage], task_id: int):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        task = await self.task_repository.get_by_task_id(task_id)
        task_deadline_datetime = task.deadline_datetime            
        if task_deadline_datetime:
            messages = [
                {"role": "system", "content": f"deadline_date: {task_deadline_datetime.strftime('%d.%m.%Y')}\ndeadline_time: {task_deadline_datetime.strftime('%H:%M')}"},
                {"role": "user", "content": f"П ({sender_name}): {message.text}"}
            ]
        else:
            messages = [
                {"role": "system", "content": f"deadline_date: None\ndeadline_time: None"},
                {"role": "user", "content": f"П ({sender_name}): {message.text}"}
            ]
        new_task_deadline_datetime = await self.task_assistant.change_task_deadline(messages)
        if new_task_deadline_datetime:
            task.deadline_datetime = new_task_deadline_datetime
            await self.task_repository.set_deadline(task_id, new_task_deadline_datetime)
            if task.author_id != task.executor_id and task.status in ["pending", "active"]:
                await self.task_notification_service.send_deadline_changed(task)
    