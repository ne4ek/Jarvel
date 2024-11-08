from application.providers.repositories_provider import RepositoriesDependencyProvider
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from domain.entities.task import Task
from datetime import datetime
from icecream import ic

class TaskMenuService:
    def __init__(self, repository_provider: RepositoriesDependencyProvider):
        self.task_repository = repository_provider.get_tasks_repository()
        self.user_chat_repository = repository_provider.get_user_chats_repository()
        self.companies_repository = repository_provider.get_companies_repository()
        self.users_repository = repository_provider.get_users_repository()
    
    
    async def get_company_keyboard(self, user_id: int):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        companies_codes = await self.companies_repository.get_companies_codes_by_user_id(user_id)
        ic(companies_codes)
        for company_code in companies_codes:
            text = await self.companies_repository.get_name_by_company_code(company_code[0])
            keyboard.inline_keyboard.append(
                [InlineKeyboardButton(text=text,
                                    callback_data=f"user_go_to choose_task_type company_code:{company_code[0]}")]
            )
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")])
        return keyboard      


    def get_task_type_keyboard(self, company_code: str):
        
        keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Полученные", callback_data=f"user_go_to menu_tasks company_code:{company_code}")],
            [InlineKeyboardButton(text="Поставленные", callback_data=f"user_go_to menu_orders company_code:{company_code}")],
            [InlineKeyboardButton(text="Личные задачи", callback_data=f"user_go_to p_tasks company_code:{company_code}")],
            [InlineKeyboardButton(text="Архив", callback_data=f"user_go_to menu_task_archive company_code:{company_code}")],
            [InlineKeyboardButton(text="К выбору компании", callback_data="user_go_to tasks_choose_company"),
            InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]
        ])
        return keyboard
    
    def get_archive_task_type_keyboard(self, company_code: str):
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Полученные", callback_data=f"user_go_to archive_tasks company_code:{company_code}")],
            [InlineKeyboardButton(text="Поставленные", callback_data=f"user_go_to archive_orderss company_code:{company_code}")],
            [InlineKeyboardButton(text="Личные задачи", callback_data=f"user_go_to archive_p_tasks company_code:{company_code}")],
            [InlineKeyboardButton(text="<<", callback_data=f"user_go_to choose_task_type company_code:{company_code}"), InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]
        ])
        return {"text": "Выберите тип задач", "keyboard": keyboard}
    
    async def get_order_list(self, user_id: int, company_code: str):
        tasks = await self.task_repository.get_by_author(author_id=user_id, company_code=company_code)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        if not tasks:
            text = "Поставленных вами задач не найдено!"
            keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="К выбору типа задач", callback_data=f"user_go_to choose_task_type company_code:{company_code}")],
                                             [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
            return {"text": text, "keyboard": keyboard}
        indentation = " " * (len(tasks) - 3)
        
        text = ""
        task_summary = \
        """
{n}. 📝{task}
{indentation}🔤Тег: {tag}
{indentation}🕒Срок: {deadline}
{indentation}👤Исполнитель: {executor}
{indentation}📊 Статус: {task_status}
----------------------------------
        """
        keyboard.inline_keyboard.append([])
        keyboard_row = 0
        
        for n, task in enumerate(tasks):
            # ic(task)
            deadline: datetime = task.deadline_datetime
            deadline_format = deadline.strftime("%d.%m.%Y в %H:%M")
            status = self.__get_status_string(task.status)
            task_text = task_summary.format(
                n=n+1,
                task=task.task,
                indentation=indentation,
                tag=task.tag,
                deadline=deadline_format,
                executor=f"{task.executor_user.full_name} ({task.executor_user.username})",
                task_status=status
            )
            text += task_text
            keyboard.inline_keyboard[keyboard_row].append(InlineKeyboardButton(text=f"{n + 1}", callback_data=f"user_go_to order_id:{task.task_id}"))
            if (n + 1) % 5 == 0:
                keyboard_row += 1
                keyboard.inline_keyboard.append([])
        keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="К выбору типа задач", callback_data=f"user_go_to choose_task_type company_code:{company_code}")],
                                         [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
        return {"text": text, "keyboard": keyboard}
    
    async def get_task_list(self, user_id: int, company_code: str):
        tasks = await self.task_repository.get_by_executor(user_id, company_code=company_code)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        if not tasks:
            text = "Поставленных вам задач не найдено!"
            keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="К выбору типа задач", callback_data=f"user_go_to choose_task_type company_code:{company_code}")],
                                             [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
            return {"text": text, "keyboard": keyboard}
        indentation = " " * (len(tasks) - 3)
    
        text = ""
        task_summary = \
        """
{n}. 📝{task}
{indentation}🔤Тег: {tag}
{indentation}🕒Срок: {deadline}
{indentation}👤Автор: {author}
----------------------------------
        """
    

        keyboard.inline_keyboard.append([])
        keyboard_row = 0
        
        for n, task in enumerate(tasks):
            # ic(task)
            deadline: datetime = task.deadline_datetime
            deadline_format = deadline.strftime("%d.%m.%Y в %H:%M")
            author = await self.users_repository.get_username_by_id(task.author_id)
            task_text = task_summary.format(
                n=n+1,
                task=task.task,
                indentation=indentation,
                tag=task.tag,
                deadline=deadline_format,
                author=author
            )
            text += task_text
            keyboard.inline_keyboard[keyboard_row].append(InlineKeyboardButton(text=f"{n + 1}", callback_data=f"user_go_to task_id:{task.task_id}"))
            if (n + 1) % 5 == 0:
                keyboard_row += 1
                keyboard.inline_keyboard.append([])
        keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="К выбору типа задач", callback_data=f"user_go_to choose_task_type company_code:{company_code}")],
                                         [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
        return {"text": text, "keyboard": keyboard}
    
    async def get_personal_task_list(self, user_id: int, company_code: str):
        tasks = await self.task_repository.get_personal_tasks(user_id, company_code=company_code)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        
        if not tasks:
            text = "Персональных задач не найдено!"
            keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="К выбору типа задач", callback_data=f"user_go_to choose_task_type company_code:{company_code}")],
                                             [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
            return {"text": text, "keyboard": keyboard}
        indentation = " " * (len(tasks) - 3)
    
        text = ""
        task_summary = \
        """
{n}. 📝{task}
{indentation}🔤Тег: {tag}
{indentation}🕒Срок: {deadline}
----------------------------------
        """
    

        keyboard.inline_keyboard.append([])
        keyboard_row = 0
        
        for n, task in enumerate(tasks):
            # ic(task)
            deadline: datetime = task.deadline_datetime
            deadline_format = deadline.strftime("%d.%m.%Y в %H:%M")
            task_text = task_summary.format(
                n=n+1,
                task=task.task,
                indentation=indentation,
                tag=task.tag,
                deadline=deadline_format,
            )
            text += task_text
            keyboard.inline_keyboard[keyboard_row].append(InlineKeyboardButton(text=f"{n + 1}", callback_data=f"user_go_to p_task_id:{task.task_id}"))
            if (n + 1) % 5 == 0:
                keyboard_row += 1
                keyboard.inline_keyboard.append([])
        keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="К выбору типа задач", callback_data=f"user_go_to choose_task_type company_code:{company_code}")],
                                         [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
        return {"text": text, "keyboard": keyboard}
    
    async def get_archive_task_list(self, executor_id: int, company_code: str):
        tasks = await self.task_repository.get_archived_executor(executor_id, company_code=company_code)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        if not tasks:
            text = "Поставленных вам задач не найдено!"
            keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="К выбору типа задач", callback_data=f"user_go_to choose_task_type company_code:{company_code}")],
                                             [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
            return {"text": text, "keyboard": keyboard}
        indentation = " " * (len(tasks) - 3)
    
        text = ""
        task_summary = \
        """
{n}. 📝{task}
{indentation}🔤Тег: {tag}
{indentation}🕒Срок: {deadline}
{indentation}👤Автор: {author}
----------------------------------
        """
    

        keyboard.inline_keyboard.append([])
        keyboard_row = 0
        
        for n, task in enumerate(tasks):
            # ic(task)
            deadline: datetime = task.deadline_datetime
            deadline_format = deadline.strftime("%d.%m.%Y в %H:%M")
            author = await self.users_repository.get_username_by_id(task.author_id)
            task_text = task_summary.format(
                n=n+1,
                task=task.task,
                indentation=indentation,
                tag=task.tag,
                deadline=deadline_format,
                author=author
            )
            text += task_text
            keyboard.inline_keyboard[keyboard_row].append(InlineKeyboardButton(text=f"{n + 1}", callback_data=f"user_go_to task_id:{task.task_id}"))
            if (n + 1) % 5 == 0:
                keyboard_row += 1
                keyboard.inline_keyboard.append([])
        keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="К выбору типа задач", callback_data=f"user_go_to choose_task_type company_code:{company_code}")],
                                         [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
        return {"text": text, "keyboard": keyboard}
    
    async def get_archive_order_list(self, user_id: int, company_code: str):
        tasks = await self.task_repository.get_archived_author(user_id, company_code=company_code)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        if not tasks:
            text = "Поставленных вами задач не найдено!"
            keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="К выбору типа задач", callback_data=f"user_go_to choose_task_type company_code:{company_code}")],
                                             [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
            return {"text": text, "keyboard": keyboard}
        indentation = " " * (len(tasks) - 3)
        
        text = ""
        task_summary = \
        """
{n}. 📝{task}
{indentation}🔤Тег: {tag}
{indentation}🕒Срок: {deadline}
{indentation}👤Исполнитель: {executor}
----------------------------------
        """
        
        keyboard.inline_keyboard.append([])
        keyboard_row = 0
        
        for n, task in enumerate(tasks):
            # ic(task)
            deadline: datetime = task.deadline_datetime
            deadline_format = deadline.strftime("%d.%m.%Y в %H:%M")
            status = self.__get_status_string(task.status)
            task_text = task_summary.format(
                n=n+1,
                task=task.task,
                indentation=indentation,
                tag=task.tag,
                deadline=deadline_format,
                executor=f"{task.executor_user.full_name} ({task.executor_user.username})",
                task_status=status
            )
            text += task_text
            keyboard.inline_keyboard[keyboard_row].append(InlineKeyboardButton(text=f"{n + 1}", callback_data=f"user_go_to order_id:{task.task_id}"))
            if (n + 1) % 5 == 0:
                keyboard_row += 1
                keyboard.inline_keyboard.append([])
        keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="К выбору типа задач", callback_data=f"user_go_to choose_task_type company_code:{company_code}")],
                                         [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
        return {"text": text, "keyboard": keyboard}
    
    async def get_archive_personal_task_list(self, user_id: int, company_code: str):
        tasks = await self.task_repository.get_archived_personal_tasks(user_id, company_code=company_code)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        
        
        if not tasks:
            text = "Персональных задач не найдено!"
            keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="К выбору типа задач", callback_data=f"user_go_to choose_task_type company_code:{company_code}")],
                                             [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
            return {"text": text, "keyboard": keyboard}
        indentation = " " * (len(tasks) - 3)
    
        text = ""
        task_summary = \
        """
{n}. 📝{task}
{indentation}🔤Тег: {tag}
{indentation}🕒Срок: {deadline}
----------------------------------
        """
    
        keyboard.inline_keyboard.append([])
        keyboard_row = 0
        ic(tasks)
        for n, task in enumerate(tasks):
            # ic(task)
            deadline: datetime = task.deadline_datetime
            deadline_format = deadline.strftime("%d.%m.%Y в %H:%M")
            task_text = task_summary.format(
                n=n+1,
                task=task.task,
                indentation=indentation,
                tag=task.tag,
                deadline=deadline_format,
            )
            text += task_text
            if (n % 5) == 0:
                keyboard_row += 1
                keyboard.inline_keyboard.append([])
        
        keyboard.inline_keyboard[keyboard_row].append(InlineKeyboardButton(text=f"{n + 1}", callback_data=f"user_go_to p_task_id:{task.task_id}"))
        keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="К выбору типа задач", callback_data=f"user_go_to choose_task_type company_code:{company_code}")],
                                         [InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
        return {"text": text, "keyboard": keyboard}
    
    async def get_task_menu(self, task_id: int):
        task: Task = await self.task_repository.get_by_task_id(task_id)
        task_text = \
'''
📝 Краткое описание: {task_summary}
🔤 Тэг: {tag}
📄 Описание:\n{task}\n\n
🕒 Дедлайн: {deadline}
👤 Автор: {author}

📊 Статус: {task_status}
'''
        deadline: datetime = task.deadline_datetime
        deadline_format = deadline.strftime("%d.%m.%Y в %H:%M")
        task_status = self.__get_status_string(task.status)
        task_text = task_text.format(task_summary=task.task_summary,
                                     tag=task.tag,
                                     task=task.task,
                                     deadline=deadline_format,
                                     author=f"{task.author_user.full_name} ({task.author_user.username})",
                                     task_status=task_status)
        
        if task_status in ["в работе", "просрочена"]:
            change_status_button = InlineKeyboardButton(text="Отметить выполненной", callback_data=f"task_set_complete task_id:{task.task_id}")
        elif task_status in ["завершена", "ожидает подтверждения"]:
            change_status_button = InlineKeyboardButton(text="Изменить на 'в работе'", callback_data=f"task_set_active task_id:{task.task_id}")
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[change_status_button]])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="К списку задач", callback_data=f"user_go_to menu_tasks company_code:{task.company_code}"), InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")])
        
        return {"text": task_text, "keyboard": keyboard}
    
    async def get_order_menu(self, order_id: int):
        task: Task = await self.task_repository.get_by_task_id(order_id)
        
        
        task_text = \
'''
📝 Краткое описание: {task_summary}
🔤 Тэг: {tag}
📄 Описание:\n{task}\n\n
🕒 Дедлайн: {deadline}
👤 Исполнитель: {executor}

📊 Статус: {task_status}
'''
        deadline: datetime = task.deadline_datetime
        deadline_format = deadline.strftime("%d.%m.%Y в %H:%M МСК")
        task_status = self.__get_status_string(task.status)
        task_text = task_text.format(task_summary=task.task_summary,
                                     tag=task.tag,
                                     task=task.task,
                                     deadline=deadline_format,
                                     executor=f"{task.executor_user.full_name} ({task.executor_user.username})",
                                     task_status=task_status)
        
        if task.status in ["complete", "cancelled"]:
            # ic(task.task_id)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='Вернуть в работу', callback_data=f"order_set_pending task_id:{task.task_id}")]])
            menu_type = "archive_orders"
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отменить заказ", callback_data=f"order_set_cancelled order_id:{task.task_id}")]])
            menu_type = "menu_orders"
        keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="Изменить описание", callback_data=f"order_change description order_id:{task.task_id}")],
                                         [InlineKeyboardButton(text="Изменить тег", callback_data=f"order_change tag order_id:{task.task_id}")],
                                         [InlineKeyboardButton(text="Перенести дедлайн", callback_data=f"order_change deadline order_id:{task.task_id}")],
                                         [InlineKeyboardButton(text="К списку заказов", callback_data=f"user_go_to {menu_type} company_code:{task.company_code}"),
                                          InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
        return {"text": task_text, "keyboard": keyboard}
    
    async def get_personal_task_menu(self, p_task_id: int):
        task: Task = await self.task_repository.get_by_task_id(p_task_id)
        # ic(task)
        task_text = \
            '''
📝 Краткое описание: {task_summary}
🔤 Тэг: {tag}
📄 Описание:\n{task}\n\n
🕒 Дедлайн: {deadline}
📊 Статус: {task_status}
            '''
        deadline: datetime = task.deadline_datetime
        deadline_format = deadline.strftime("%d.%m.%Y в %H:%M МСК")
        task_status = self.__get_status_string(task.status)
        task_text = task_text.format(task_summary=task.task_summary,
                                     tag=task.tag,
                                     task=task.task,
                                     deadline=deadline_format,
                                     task_status=task_status)
        if task.status == "active":
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Отметить выполненной", callback_data=f"p_task_set_complete p_task_id:{task.task_id}")]])
            keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="Изменить описание", callback_data=f"p_task_change description p_task_id:{task.task_id}")],
                                             [InlineKeyboardButton(text="Изменить тег", callback_data=f"p_task_change tag p_task_id:{task.task_id}")],
                                             [InlineKeyboardButton(text="Перенести дедлайн", callback_data=f"p_task_change deadline p_task_id:{task.task_id}")],
                                             [InlineKeyboardButton(text="К списку задач", callback_data=f"user_go_to p_tasks company_code:{task.company_code}")]])
        else:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Вернуть в работу", callback_data=f"p_task_set_active p_task_id:{task.task_id}")]])
            # ic(task.task_id)
            keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="Изменить описание", callback_data=f"p_task_change description p_task_id:{task.task_id}")],
                                            [InlineKeyboardButton(text="Изменить тег", callback_data=f"p_task_change tag p_task_id:{task.task_id}")],
                                            [InlineKeyboardButton(text="Перенести дедлайн", callback_data=f"p_task_change deadline p_task_id:{task.task_id}")],
                                            [InlineKeyboardButton(text="К списку задач", callback_data=f"user_go_to archive_p_tasks company_code:{task.company_code}"), 
                                             InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
    
        return {"text": task_text, "keyboard": keyboard}
    
    async def mark_task_complete(self, task_id: int):
        task: Task = await self.task_repository.get_by_task_id(task_id)
        
        task.status = "complete"
        
        task_text = \
'''
📝 Краткое описание: {task_summary}
🔤 Тэг: {tag}
📄 Описание:\n{task}\n\n
🕒 Дедлайн: {deadline}
👤 Автор: {author}

📊 Статус: {task_status}
'''
        task_status = self.__get_status_string(task.status)
        deadline: datetime = task.deadline_datetime
        deadline_format = deadline.strftime("%d.%m.%Y в %H:%M")
        task_text = task_text.format(task_summary=task.task_summary,
                                     tag=task.tag,
                                     task=task.task,
                                     deadline=deadline_format,
                                     author=f"{task.author_user.full_name} ({task.author_user.username})",
                                     task_status=task_status)
        
        if task.author_id == task.executor_id:
            text=None
        else:
            executor_username = await self.users_repository.get_username_by_id(task.executor_id)
            text = f'Сотрудник {executor_username} завершил задачу!\nЗадача: {task.task_summary}\nТэг: {task.tag}'
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text='Изменить на "в работе"', callback_data=f"task_set_active task_id:{task.task_id}")])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="К списку задач", callback_data=f"user_go_to menu_tasks company_code:{task.company_code}"), InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")])
        
        await self.task_repository.set_status(task_id=task_id, status="complete")
        
        return {"text": task_text, "keyboard": keyboard, "author_text": text, "author_id": task.author_id}
    
    async def mark_task_active(self, task_id: int):
        task: Task = await self.task_repository.get_by_task_id(task_id)
        
        task.status = "active"
        
        task_text = \
'''
📝 Краткое описание: {task_summary}
🔤 Тэг: {tag}
📄 Описание:\n{task}\n\n
🕒 Дедлайн: {deadline}
👤 Автор: {author}

📊 Статус: {task_status}
'''
        task_status = self.__get_status_string(task.status)
        deadline: datetime = task.deadline_datetime
        deadline_format = deadline.strftime("%d.%m.%Y в %H:%M")
        task_text = task_text.format(task_summary=task.task_summary,
                                     tag=task.tag,
                                     task=task.task,
                                     deadline=deadline_format,
                                     author=f"{task.author_user.full_name} ({task.author_user.username})",
                                     task_status=task_status)
        
        if task.author_id == task.executor_id:
            text=None
        else:    
            executor_username = await self.users_repository.get_username_by_id(task.executor_id)
            text = f'Сотрудник {executor_username} сменил статус задачи на "в работе"!\nЗадача: {task.task_summary}\nТэг: {task.tag}'
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text='Отметить выполненной', callback_data=f"task_set_complete task_id:{task.task_id}")])
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="К списку задач", callback_data=f"user_go_to menu_tasks company_code:{task.company_code}"), InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")])
        
        await self.task_repository.set_status(task_id=task_id, status="active")
        
        return {"text": task_text, "keyboard": keyboard, "author_text": text, "author_id": task.author_id}
    
    async def mark_order_cancelled(self, order_id: int):
        task: Task = await self.task_repository.get_by_task_id(order_id)
        
        await self.task_repository.set_status(task_id=order_id, status="complete")
        
        task_text = \
'''
📝 Краткое описание: {task_summary}
🔤 Тэг: {tag}
📄 Описание:\n{task}\n\n
🕒 Дедлайн: {deadline}
👤 Исполнитель: {executor}

📊 Статус: {task_status}
'''
        task_status = self.__get_status_string("cancelled")
        deadline: datetime = task.deadline_datetime
        deadline_format = deadline.strftime("%d.%m.%Y в %H:%M")
        task_text = task_text.format(task_summary=task.task_summary,
                                     tag=task.tag,
                                     task=task.task,
                                     deadline=deadline_format,
                                     executor=f"{task.executor_user.full_name} ({task.executor_user.username})",
                                     task_status=task_status)
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        # ic(task.task_id)
        keyboard.inline_keyboard.append([InlineKeyboardButton(text='Вернуть в работу', callback_data=f"order_set_pending task_id:{task.task_id}")])
        
        keyboard.inline_keyboard.append([InlineKeyboardButton(text="К списку заказов", callback_data=f"user_go_to menu_orders company_code:{task.company_code}"), InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")])
        
        text = f'Заказчик {task.author_user.username} отменил задачу "{task.task_summary}"!'
        
        return {"text": task_text, "keyboard": keyboard, "executor_text": text, "executor_id": task.executor_id}
    
    async def mark_order_pending(self, order_id: int):
        task: Task = await self.task_repository.get_by_task_id(order_id)
        
        await self.task_repository.set_status(order_id, "pending")
        task_text = \
'''
📝 Краткое описание: {task_summary}
🔤 Тэг: {tag}
📄 Описание:\n{task}\n\n
🕒 Дедлайн: {deadline}
👤 Исполнитель: {executor}

📊 Статус: {task_status}
'''
        task_status = self.__get_status_string("pending")
        deadline: datetime = task.deadline_datetime
        deadline_format = deadline.strftime("%d.%m.%Y в %H:%M")
        task_text = task_text.format(task_summary=task.task_summary,
                                     tag=task.tag,
                                     task=task.task,
                                     deadline=deadline_format,
                                     executor=f"{task.executor_user.full_name} ({task.executor_user.username})",
                                     task_status=task_status)
        keyboard = InlineKeyboardMarkup(inline_keyboard=[])
        keyboard.inline_keyboard.extend([[InlineKeyboardButton(text="Отменить заказ", callback_data=f"order_set_cancelled order_id:{task.task_id}")],
                                         [InlineKeyboardButton(text="Изменить описание", callback_data=f"order_change description order_id:{task.task_id}")],
                                         [InlineKeyboardButton(text="Изменить тег", callback_data=f"order_change tag order_id:{task.task_id}")],
                                         [InlineKeyboardButton(text="Перенести дедлайн", callback_data=f"order_change deadline order_id:{task.task_id}")],
                                         [InlineKeyboardButton(text="К списку заказов", callback_data=f"user_go_to menu_orders company_code:{task.company_code}"), InlineKeyboardButton(text="В главное меню", callback_data="user_go_to main_menu")]])
        text_for_executor = \
f'''Заказчик {task.author_user.username} вернул в работу задачу "{task.task_summary}"!
🔤 Тэг: {task.tag}
📄 Описание:\n{task.task}\n\n
🕒 Дедлайн: {deadline_format}'''
        keyboard_executor = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Принять", callback_data=f"user accept_task task_id:{task.task_id}")]])
        return {"author_text": task_text, "author_keyboard": keyboard, "executor_text": text_for_executor, "executor_keyboard": keyboard_executor, "executor_id": task.executor_id}
    
    async def mark_personal_task_complete(self, p_task_id: int):
        await self.task_repository.set_status(task_id=p_task_id,
                                        status="complete")
        return await self.get_personal_task_menu(p_task_id=p_task_id)
    
    async def mark_personal_task_active(self, p_task_id: int):
        await self.task_repository.set_status(task_id=p_task_id,
                                        status="active")
        return await self.get_personal_task_menu(p_task_id=p_task_id)
    
    def __get_status_string(self, status):
        if status == "active":
            return "в работе"
        elif status == "complete":
            return "завершена"
        elif status == "overdue":
            return "просрочена"
        elif status == "cancelled":
            return "отменена"
        elif status == "pending":
            return "ожидает подтверждения"
        
    