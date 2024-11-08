from application.providers.repositories_provider import RepositoriesDependencyProvider
from .task_scheduler_job_service import TaskJobService
from .send_task_notification_service import SendTaskNotificationService
from aiogram import types
from aiogram.fsm.context import FSMContext
from domain.contracts.assistant import Assistant
from domain.entities.transcribed_message import TranscribedMessage
from domain.entities.task import Task
from typing import Union
from datetime import timedelta
from icecream import ic

class TelegramComposeTaskService:
    def __init__(self, repository_provider: RepositoriesDependencyProvider, task_assistant: Assistant, task_notification_sender: SendTaskNotificationService, task_job_service: TaskJobService):
        self.task_assistant = task_assistant
        self.task_notification_sender = task_notification_sender
        self.company_repository = repository_provider.get_companies_repository()
        self.task_job_service = task_job_service
        self.user_repository = repository_provider.get_users_repository()
        self.task_repository = repository_provider.get_tasks_repository()

    async def change_task_author(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        if data:
            task: Task = data.get("task").get("entity")
            bot_message = data.get("task").get("message")
            task_author_user = task.author_user
            if task_author_user:
                task_author_name = task_author_user.full_name
            else:
                task_author_name = None
            
            messages = [
                {"role": "system", "content": f"task_author_name: {task_author_name}"},
                {"role": "user", "content": f"П ({sender_name}): {message.text}"}
            ]
            company_code = await self.__get_company_code(message.chat.id)
            new_task_author_user = await self.task_assistant.change_task_author(messages, company_code)
            task.author_user = new_task_author_user
            await state.update_data({"task": {"entity": task, "message": bot_message}})
            return self.task_assistant.compose_telegram_filling_message(task)

    async def change_task_executor(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        task: Task = data.get("task").get("entity")
        bot_message = data.get("task").get("message")
        task_executor_user = task.executor_user
        if task_executor_user:
            task_executor_name = task_executor_user.full_name
        else:
            task_executor_name = None
        
        messages = [
            {"role": "system", "content": f"task_executor_name: {task_executor_name}"},
            {"role": "user", "content": f"П ({sender_name}): {message.text}"}
        ]
        company_code = await self.__get_company_code(message.chat.id)
        new_task_executor_user = await self.task_assistant.change_task_executor(messages, company_code)
        task.executor_user = new_task_executor_user
        await state.update_data({"task": {"entity": task, "message": bot_message}})
        return self.task_assistant.compose_telegram_filling_message(task)
        
    async def change_task_deadline(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        task: Task = data.get("task").get("entity")
        bot_message = data.get("task").get("message")
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
        task.deadline_datetime = new_task_deadline_datetime
        await state.update_data({"task": {"entity": task, "message": bot_message}})
        return self.task_assistant.compose_telegram_filling_message(task)
    
    async def change_task_description(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        sender_name = await self.__get_message_sender_full_name(message.from_user.id)
        data = await state.get_data()
        
        task: Task = data.get("task").get("entity")
        bot_message = data.get("task").get("message")
        
        task_description = task.task
        task_summary = task.task_summary
        task_tag = task.tag
        if task_tag in ("None", "0"):
            task_tag = None
        if task_summary in ("None", "0"):
            task_summary = None
        
        messages = [
            {"role": "system", "content": f"task: {task_description}\ntask_summary: {task_summary}\ntag: {task_tag}"},
            {"role": "system", "content": f"П ({sender_name}): {message.text}"}
        ]
        new_task_description: dict = await self.task_assistant.change_task_description(messages)
        
        
        new_task_summary = new_task_description.get("task_summary")
        new_task_tag = new_task_description.get("tag").upper()
        new_task = new_task_description.get("task")
        if new_task == "0":
            new_task = None
        if new_task_summary == "0":
            new_task_summary = None
        if new_task_tag == "0":
            new_task_tag = None
        task.task = new_task
        task.task_summary = new_task_summary
        task.tag = new_task_tag
        
        await state.update_data({"task": {"entity": task, "message": bot_message}})
        return self.task_assistant.compose_telegram_filling_message(task)
    
    async def change_task_tag(self, message: Union[types.Message, TranscribedMessage], state: FSMContext):
        data = await state.get_data()
        
        bot_message = data.get("task").get("message")
        task: Task = data.get("task").get("entity")
        
        task.tag = message.text.upper()
        
        await state.update_data({"task": {"entity": task, "message": bot_message}})
        return self.task_assistant.compose_telegram_filling_message(task)
    
    async def save_task(self, state: FSMContext):
        data = await state.get_data()
        task: Task = data.get("task").get("entity")
        if not task.tag:
            task.tag = "-"
        if not task.status:
            if task.executor_id == task.author_id:
                task.status = "active"
            else:
                task.status = "pending"
        
        task_id = await self.task_repository.save(task)
        task.task_id = task_id
        self.task_job_service.add_saved_task_jobs(task)
        
        await self.task_notification_sender.send_task_is_set(task)
        
    async def get_telegram_message(self, state: FSMContext):
        data = await state.get_data()
        if data:
            task: Task = data.get("task").get("entity")
            # ic(task)
            return self.task_assistant.compose_telegram_filling_message(task)
    
    async def __get_company_code(self, chat_id: int):
        return await self.company_repository.get_company_code_by_chat_id(chat_id)
    
    async def __get_message_sender_full_name(self, user_id: int):
        return await self.user_repository.get_full_name_by_id(user_id=user_id)