from typing import List, Union

from application.repositories.tasks_repository import TasksRepository
from application.repositories.users_repository import UsersRepository
from domain.entities.task import Task
from psycopg2.pool import ThreadedConnectionPool

from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection
import pytz
from const import TASK_STATUSES, ARCHIVE_TASK_STATUSES, PERSONAL_TASK_STATUSES, ORDER_STATUSES
from datetime import datetime


class PostgresTasksRepository(TasksRepository):
    def __init__(self, db_connection_pool: ThreadedConnectionPool, users_repository: UsersRepository):
        self.db_connection_pool = db_connection_pool
        self.users_repository = users_repository

    @open_and_close_connection
    def save(self, task: Task, conn=None, cursor=None) -> int:
        cursor.execute(
            'INSERT INTO tasks (executor_id, author_id, task, task_summary, deadline, status, tag, company_code)'
            'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
            'RETURNING task_id;',
            (task.executor_user.user_id,
             task.author_user.user_id,
             task.task,
             task.task_summary,
             task.deadline_datetime,
             task.status,
             task.tag,
             task.company_code))
        task_id = cursor.fetchone()[0]
        conn.commit()
        return task_id

    @open_and_close_connection
    def get_by_task_id(self, task_id: int, conn=None, cursor=None) -> Task:
        cursor.execute(f'SELECT * FROM tasks WHERE task_id = {task_id}')
        row = cursor.fetchone()
        task = Task(*row)
        local_tz = pytz.timezone('Europe/Moscow')
        task.deadline_datetime = task.deadline_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
        task.author_user = self.users_repository.get_by_id(row[1])
        task.executor_user = self.users_repository.get_by_id(row[2])
        return task

    @open_and_close_connection
    def get_all(self, conn=None, cursor=None) -> List[Task]:
        cursor.execute("SELECT * FROM tasks")
        rows = cursor.fetchall()
        list_of_tasks = []
        for row in rows:
            task = Task(*row)
            local_tz = pytz.timezone('Europe/Moscow')
            task.deadline_datetime = task.deadline_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            list_of_tasks.append(task)
        return list_of_tasks

    @open_and_close_connection
    def get_by_company(self, company_code: str, conn=None, cursor=None) -> List[Task]:
        cursor.execute(f"SELECT * FROM tasks WHERE company_code = '{company_code}';")
        rows = cursor.fetchall()
        list_of_tasks = []
        for row in rows:
            task = Task(*row)
            local_tz = pytz.timezone('Europe/Moscow')
            task.deadline_datetime = task.deadline_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            task.author_user = self.users_repository.get_by_id(row[1])
            task.executor_user = self.users_repository.get_by_id(row[2])
            list_of_tasks.append(task)
        return list_of_tasks

    @open_and_close_connection
    def get_by_executor(self, executor_id: int, company_code: str, conn=None, cursor=None) -> List[Task]:
        cursor.execute(f"SELECT * FROM tasks WHERE status IN {tuple(TASK_STATUSES)} AND executor_id = '{executor_id}' AND company_code = '{company_code}' AND executor_id != author_id;")
        rows = cursor.fetchall()
        list_of_tasks = []
        for row in rows:
            task = Task(*row)
            local_tz = pytz.timezone('Europe/Moscow')
            task.deadline_datetime = task.deadline_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            task.author_user = self.users_repository.get_by_id(row[1])
            task.executor_user = self.users_repository.get_by_id(row[2])
            list_of_tasks.append(task)
        return list_of_tasks

    @open_and_close_connection
    def get_by_author(self, author_id: int, company_code: str, conn=None, cursor=None) -> List[Task]:
        cursor.execute(f"SELECT * FROM tasks WHERE status IN {tuple(ORDER_STATUSES)} AND author_id = '{author_id}' AND company_code = '{company_code}' AND executor_id != author_id;")
        rows = cursor.fetchall()
        list_of_tasks = []
        for row in rows:
            task = Task(*row)
            local_tz = pytz.timezone('Europe/Moscow')
            task.deadline_datetime = task.deadline_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            task.author_user = self.users_repository.get_by_id(row[1])
            task.executor_user = self.users_repository.get_by_id(row[2])
            list_of_tasks.append(task)
        return list_of_tasks
    
    @open_and_close_connection
    def get_personal_tasks(self, user_id: int, company_code: str, conn=None, cursor=None) -> List[Task]:
        if len(PERSONAL_TASK_STATUSES) == 1:
            cursor.execute(f"SELECT * FROM tasks WHERE status = '{PERSONAL_TASK_STATUSES[0]}' AND author_id = '{user_id}' AND company_code = '{company_code}' AND executor_id = author_id;")
        else:
            cursor.execute(f"SELECT * FROM tasks WHERE status IN {tuple(PERSONAL_TASK_STATUSES)} AND author_id = '{user_id}' AND company_code = '{company_code}' AND executor_id = author_id;")
        rows = cursor.fetchall()
        list_of_tasks = []
        for row in rows:
            task = Task(*row)
            local_tz = pytz.timezone('Europe/Moscow')
            task.deadline_datetime = task.deadline_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            task.author_user = self.users_repository.get_by_id(row[1])
            task.executor_user = self.users_repository.get_by_id(row[2])
            list_of_tasks.append(task)
        return list_of_tasks

    @open_and_close_connection
    def get_archived_author(self, author_id: int, company_code: str, conn=None, cursor=None) -> List[Task]:
        if len(ARCHIVE_TASK_STATUSES) == 1:
            cursor.execute(
                f"SELECT * FROM tasks WHERE status = '{ARCHIVE_TASK_STATUSES[0]}' AND company_code = '{company_code}' AND author_id = {author_id} AND executor_id != author_id;")
        else:
            cursor.execute(
                f"SELECT * FROM tasks WHERE status IN {tuple(ARCHIVE_TASK_STATUSES)} AND company_code = '{company_code}' AND author_id = {author_id} AND executor_id != author_id;")
        rows = cursor.fetchall()
        list_of_tasks = []
        for row in rows:
            task = Task(*row)
            local_tz = pytz.timezone('Europe/Moscow')
            task.deadline_datetime = task.deadline_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            task.author_user = self.users_repository.get_by_id(row[1])
            task.executor_user = self.users_repository.get_by_id(row[2])
            list_of_tasks.append(task)
        return list_of_tasks

    @open_and_close_connection
    def get_archived_executor(self, executor_id: int, company_code: str, conn=None, cursor=None) -> List[Task]:
        cursor.execute(
            f"SELECT * FROM tasks WHERE status IN {tuple(ARCHIVE_TASK_STATUSES)} AND company_code = '{company_code}' AND executor_id = {executor_id} AND executor_id != author_id;")
        rows = cursor.fetchall()
        list_of_tasks = []
        for row in rows:
            task = Task(*row)
            local_tz = pytz.timezone('Europe/Moscow')
            task.deadline_datetime = task.deadline_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            task.author_user = self.users_repository.get_by_id(row[1])
            task.executor_user = self.users_repository.get_by_id(row[2])
            list_of_tasks.append(task)
        return list_of_tasks

    @open_and_close_connection
    def get_archived_personal_tasks(self, user_id: int, company_code: str, conn=None, cursor=None) -> List[Task]:
        cursor.execute(
            f"SELECT * FROM tasks WHERE status IN {tuple(ARCHIVE_TASK_STATUSES)} AND company_code = '{company_code}' AND executor_id = {user_id} AND executor_id = author_id;")
        rows = cursor.fetchall()
        list_of_tasks = []
        for row in rows:
            task = Task(*row)
            local_tz = pytz.timezone('Europe/Moscow')
            task.deadline_datetime = task.deadline_datetime.replace(tzinfo=pytz.utc).astimezone(local_tz)
            task.author_user = self.users_repository.get_by_id(row[1])
            task.executor_user = self.users_repository.get_by_id(row[2])
            list_of_tasks.append(task)
        return list_of_tasks

    @open_and_close_connection
    def delete(self, task_id: int, conn=None, cursor=None) -> None:
        cursor.execute(f"DELETE FROM tasks WHERE task_id = {task_id};")
        conn.commit()

    @open_and_close_connection
    def set_status(self, task_id: int, status: str, conn=None, cursor=None):
        cursor.execute(f"UPDATE tasks SET status = '{status}' WHERE task_id = '{task_id}';")
        conn.commit()
    
    @open_and_close_connection
    def set_description(self, task_id: int, new_description: str, new_task_summary: str = None, new_task_tag: str = None, conn=None, cursor=None):
        query = "UPDATE tasks SET task = %s"
        values = [new_description]

        # Add optional fields to the query and values list
        if new_task_summary:
            query += ", task_summary = %s"
            values.append(new_task_summary)

        if new_task_tag:
            query += ", tag = %s"
            values.append(new_task_tag)

        # Complete the query with the WHERE clause
        query += " WHERE task_id = %s"
        values.append(task_id)

        # Execute the query
        cursor.execute(query, tuple(values))
        conn.commit()
    
    @open_and_close_connection
    def set_tag(self, task_id: int, tag: str, conn=None, cursor=None):
        query = "UPDATE tasks SET tag = %s WHERE task_id = %s"
        values = (tag, task_id)
        cursor.execute(query, values)
        conn.commit()
    
    @open_and_close_connection
    def set_deadline(self, task_id, deadline_datetime: datetime, conn=None, cursor=None):
        query = "UPDATE tasks SET deadline = %s WHERE task_id = %s"
        values = (deadline_datetime, task_id)
        cursor.execute(query, values)
        conn.commit()