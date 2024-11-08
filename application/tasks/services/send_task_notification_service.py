from aiogram import Bot
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from application.providers.repositories_provider import RepositoriesDependencyProvider
from domain.entities.task import Task
from datetime import datetime
import pytz

class SendTaskNotificationService:
    def __init__(self, bot: Bot, repository_provivder: RepositoriesDependencyProvider):
        self.bot = bot
        self.task_repository = repository_provivder.get_tasks_repository()
        self.user_repository = repository_provivder.get_users_repository()

    async def send_task_is_set(self, task: Task):
        if task.author_id == task.executor_id:
            executor_text = \
'''
Добавлена задача!
Дедлайн: {deadline}
Тег: {tag}
Краткое описание: {task_summary}
Задача:
{task}
'''         
            executor_text = executor_text.format(deadline=task.deadline_datetime.strftime("%d.%m.%Y в %H:%M МСК") if task.deadline_datetime else "-",
                                                 tag=task.tag,
                                                 task_summary=task.task_summary,
                                                 task=task.task)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В задачу", callback_data=f"user_go_to p_task_id:{task.task_id}")]])
        else:
            executor_text = \
    '''
Вам поставлена задача!
Автор задачи: {author_name}({author_username})
Дедлайн: {deadline}
Тег: {tag}
Краткое описание: {task_summary}
Задача:
{task}
    '''
            executor_text = executor_text.format(author_username=task.author_user.username,
                                                author_name=task.author_user.full_name,
                                                deadline=task.deadline_datetime.strftime("%d.%m.%Y в %H:%M МСК") if task.deadline_datetime else "-",
                                                tag=task.tag,
                                                task_summary=task.task_summary,
                                                task=task.task)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Принять", callback_data=f"user accept_task task_id:{task.task_id}")]])
        await self.bot.send_message(chat_id=task.executor_id, text=executor_text, reply_markup=keyboard)
    
    async def send_order_is_accepted(self, task: Task):
        author_text  = \
'''
Ваш заказ принят!
Исполнитель: {executor_name}({executor_username})
Дедлайн: {deadline}
Тег: {tag}
Краткое описание: {task_summary}
Задача:
{task}
'''
        author_text = author_text.format(executor_username=task.executor_user.username,
                                         executor_name=task.executor_user.full_name,
                                         deadline=task.deadline_datetime.strftime("%d.%m.%Y в %H:%M МСК") if task.deadline_datetime else "-",
                                         tag=task.tag,
                                         task_summary=task.task_summary,
                                         task=task.task)
        author_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В задачу", callback_data=f"user_go_to order_id:{task.task_id}")]])
        await self.bot.send_message(chat_id=task.author_id, text=author_text, reply_markup=author_keyboard)
    
    async def send_order_is_done(self, task: Task):
        pass
    
    async def send_order_is_rejected(self, task: Task):
        pass
    
    async def send_task_is_overdue(self, task: Task):
        current_datetime = datetime.now(pytz.utc).astimezone(pytz.timezone('Europe/Moscow'))
        if not (task.deadline_datetime < current_datetime and task.status not in ("complete", "cancelled", "overdue")):
            return
        await self.task_repository.set_status(task.task_id, "overdue")
        if task.author_id == task.executor_id:
            personal_task_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В задачу", callback_data=f"user_go_to p_task_id:{task.task_id}")]])
            personal_text = \
'''
Вниимание! Задача просрочена!
Дедлайн: {deadline}
Тег: {tag}
Краткое описание: {task_summary}
Задача:
{task}
'''         
            personal_text = personal_text.format(deadline=task.deadline_datetime.strftime("%d.%m.%Y в %H:%M МСК") if task.deadline_datetime else "-",
                                                 tag=task.tag,
                                                 task_summary=task.task_summary,
                                                 task=task.task)
            await self.bot.send_message(chat_id=task.executor_id, text=personal_text, reply_markup=personal_task_keyboard)
            return
        
        task.author_user = await self.user_repository.get_by_id(task.author_id)
        task.executor_user = await self.user_repository.get_by_id(task.executor_id)
        executor_text = \
'''
Вниимание! Задача просрочена!
Автор задачи: {author_name}({author_username})
Дедлайн: {deadline}
Тег: {tag}
Краткое описание: {task_summary}
Задача:
{task}
'''
        executor_text = executor_text.format(author_username=task.author_user.username,
                                             author_name=task.author_user.full_name,
                                             deadline=task.deadline_datetime.strftime("%d.%m.%Y в %H:%M МСК") if task.deadline_datetime else "-",
                                             tag=task.tag,
                                             task_summary=task.task_summary,
                                             task=task.task)
        task.status = "overdue"
        executor_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В задачу", callback_data=f"user_go_to task_id:{task.task_id}")]])
        
        await self.bot.send_message(chat_id=task.executor_id, text=executor_text, reply_markup=executor_keyboard)

        task_author_text = \
'''
Внимание! Ваш заказ был просрочен!
Исполнитель: {executor_name}({executor_username})
Дедлайн: {deadline}
Тег: {tag}
Краткое описание: {task_summary}
Задача:
{task}
'''
        task_author_text = task_author_text.format(executor_username=task.executor_user.username,
                                                   executor_name=task.executor_user.full_name,
                                                   deadline=task.deadline_datetime.strftime("%d.%m.%Y в %H:%M МСК") if task.deadline_datetime else "-",
                                                   tag=task.tag,
                                                   task_summary=task.task_summary,
                                                   task=task.task)
        author_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В задачу", callback_data=f"user_go_to order_id:{task.task_id}")]])
        await self.bot.send_message(chat_id=task.author_id, text=task_author_text, reply_markup=author_keyboard)
     
    async def send_task_reminder(self, task: Task):
        if task.status != ["active", "pending"]:
            return
        task.author_user = await self.user_repository.get_by_id(task.author_id)
        if task.author_id == task.executor_id:
            personal_task_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В задачу", callback_data=f"user_go_to p_task_id:{task.task_id}")]])
            personal_text = \
'''
Напоминаем, что у вас есть задача!
Дедлайн: {deadline}
Тег: {tag}
Краткое описание: {task_summary}
Задача:
{task}
'''         
            personal_text = personal_text.format(deadline=task.deadline_datetime.strftime("%d.%m.%Y в %H:%M МСК") if task.deadline_datetime else "-",
                                                 tag=task.tag,
                                                 task_summary=task.task_summary,
                                                 task=task.task)
            await self.bot.send_message(chat_id=task.executor_id, text=personal_text, reply_markup=personal_task_keyboard)
            return
        executor_text = \
'''
Напоминаем, что у вас есть задача!
Автор задачи: {author_name}({author_username})
Дедлайн: {deadline}
Тег: {tag}
Краткое описание: {task_summary}
Задача:
{task}
'''
        executor_text = executor_text.format(author_username=task.author_user.username,
                                             author_name=task.author_user.full_name,
                                             deadline=task.deadline_datetime.strftime("%d.%m.%Y в %H:%M МСК") if task.deadline_datetime else "-",
                                             tag=task.tag,
                                             task_summary=task.task_summary,
                                             task=task.task)
        executor_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В задачу", callback_data=f"user_go_to task_id:{task.task_id}")]])
        await self.bot.send_message(chat_id=task.executor_id, text=executor_text, reply_markup=executor_keyboard)
    
    async def send_tag_changed(self, task: Task):
        task.author_user = await self.user_repository.get_by_id(task.author_id)
        
        executor_text = \
'''
Детали задачи "{task_summary}" были изменены!
Новый тег: {tag}
'''     
        executor_text = executor_text.format(task_summary=task.task_summary,
                                             tag=task.tag)
        executor_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В задачу", callback_data=f"user_go_to task_id:{task.task_id}")]])        

        await self.bot.send_message(chat_id=task.executor_id,
                                    text=executor_text,
                                    reply_markup=executor_keyboard)
    
    async def send_deadline_changed(self, task: Task):
        task.author_user = await self.user_repository.get_by_id(task.author_id)
        
        executor_text = \
'''
Детали задачи "{task_summary}" были изменены!

Новый дедлайн: {deadline}
'''     
        executor_text = executor_text.format(task_summary=task.task_summary,
                                             deadline=task.deadline_datetime.strftime("%d.%m.%Y в %H:%M МСК") if task.deadline_datetime else "-")
        executor_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В задачу", callback_data=f"user_go_to task_id:{task.task_id}")]])        

        await self.bot.send_message(chat_id=task.executor_id,
                                    text=executor_text,
                                    reply_markup=executor_keyboard)
    
    async def send_description_changed(self, old_task: Task, new_task: Task):
        new_task.author_user = await self.user_repository.get_by_id(new_task.author_id)
        
        executor_text = f'Детали задачи "{old_task.task_summary}" были изменены!'
        if old_task.task_summary != new_task.task_summary:
            executor_text += f"\n\nКраткое описание: {new_task.task_summary}"
        if old_task.task != new_task.task:
            executor_text += f"\n\nНовое описание:\n{new_task.task}"
        if old_task.tag != new_task.tag:
            executor_text += f"\nНовый тег: {new_task.tag}"
        
        executor_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="В задачу", callback_data=f"user_go_to task_id:{new_task.task_id}")]])
        await self.bot.send_message(chat_id=new_task.executor_id,
                                    text=executor_text,
                                    reply_markup=executor_keyboard)