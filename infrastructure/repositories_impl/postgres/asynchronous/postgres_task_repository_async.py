from typing import List, Union, Optional
from domain.entities.task import Task
from application.repositories.tasks_repository import TasksRepository
from application.repositories.users_repository import UsersRepository
from application.repositories.companies_repository import CompaniesRepository
from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
import pytz
from const import TASK_STATUSES, ARCHIVE_TASK_STATUSES, PERSONAL_TASK_STATUSES, ORDER_STATUSES
from datetime import datetime
from icecream import ic

class PostgresTasksRepositoryAsync(TasksRepository):
    def __init__(self, db_connection_pool, users_repository: UsersRepository, companies_repository: CompaniesRepository):
        self.db_connection_pool = db_connection_pool
        self.users_repository = users_repository
        self.companies_repository = companies_repository

    @open_and_close_connection
    async def save(self, task: Task, connection=None) -> int:
        sql_query = (
            'INSERT INTO public.task (executor_id, author_id, description, task_summary, deadline_datetime, status, tag, company_id) '
            'VALUES ($1, $2, $3, $4, $5, $6, $7, (SELECT company_id FROM public.company WHERE company_code = $8)) '
            'RETURNING task_id;'
        )
        result = await connection.fetch(sql_query, 
                                        task.executor_id,
                                        task.author_id,
                                        task.task,
                                        task.task_summary,
                                        task.deadline_datetime,
                                        task.status,
                                        task.tag,
                                        task.company_code,)
        return result[0]['task_id'] if result else None


    @open_and_close_connection
    async def get_by_task_id(self, task_id: int, connection=None) -> Task:
        sql_query = f'SELECT * FROM public.task WHERE task_id = $1'
        result = await connection.fetchrow(sql_query, task_id)
        if result:
            task = await self._row_to_task(result)
            return task

    @open_and_close_connection
    async def get_all(self, connection=None) -> List[Task]:
        sql_query = "SELECT * FROM public.task"
        rows = await connection.fetch(sql_query)
        return await self._rows_to_tasks(rows)

    @open_and_close_connection
    async def get_by_company(self, company_code: str, connection=None) -> List[Task]:
        sql_query = (
            "SELECT * FROM public.task WHERE company_id = (SELECT company_id FROM public.company WHERE company_code = $1)"
        )
        rows = await connection.fetch(sql_query, company_code)
        return await self._rows_to_tasks(rows)

    @open_and_close_connection
    async def get_by_executor(self, executor_id: int, company_code: str, connection=None) -> List[Task]:
        sql_query = (
            f"SELECT * FROM public.task WHERE status IN {tuple(TASK_STATUSES)} AND executor_id = $1 "
            f"AND company_id = (SELECT company_id FROM public.company WHERE company_code = $2) AND executor_id != author_id"
        )
        rows = await connection.fetch(sql_query, executor_id, company_code)
        return await self._rows_to_tasks(rows)

    @open_and_close_connection
    async def get_by_author(self, author_id: int, company_code: str, connection=None) -> List[Task]:
        sql_query = (
            f"SELECT * FROM public.task WHERE status IN {tuple(ORDER_STATUSES)} AND author_id = $1 "
            f"AND company_id = (SELECT company_id FROM public.company WHERE company_code = $2) AND executor_id != author_id"
        )
        rows = await connection.fetch(sql_query, author_id, company_code)
        return await self._rows_to_tasks(rows)

    @open_and_close_connection
    async def get_personal_tasks(self, user_id: int, company_code: str, connection=None) -> List[Task]:
        if len(PERSONAL_TASK_STATUSES) == 1:
            sql_query = (
                f"SELECT * FROM public.task WHERE status = $1 AND author_id = $2 "
                f"AND company_id = (SELECT company_id FROM public.company WHERE company_code = $3) AND executor_id = author_id"
            )
            rows = await connection.fetch(sql_query, PERSONAL_TASK_STATUSES[0], user_id, company_code)
        else:
            sql_query = (
                f"SELECT * FROM public.task WHERE status IN {tuple(PERSONAL_TASK_STATUSES)} AND author_id = $1 "
                f"AND company_id = (SELECT company_id FROM public.company WHERE company_code = $2) AND executor_id = author_id"
            )
            rows = await connection.fetch(sql_query, user_id, company_code)
        return await self._rows_to_tasks(rows)

    @open_and_close_connection
    async def get_archived_author(self, author_id: int, company_code: str, connection=None) -> List[Task]:
        if len(ARCHIVE_TASK_STATUSES) == 1:
            sql_query = (
                f"SELECT * FROM public.task WHERE status = $1 "
                f"AND company_id = (SELECT company_id FROM public.company WHERE company_code = $2) AND author_id = $3"
            )
            rows = await connection.fetch(sql_query, ARCHIVE_TASK_STATUSES[0], company_code, author_id)
        else:
            sql_query = (
                f"SELECT * FROM public.task WHERE status IN {tuple(ARCHIVE_TASK_STATUSES)} "
                f"AND company_id = (SELECT company_id FROM public.company WHERE company_code = $1) AND author_id = $2"
            )
            rows = await connection.fetch(sql_query, company_code, author_id)
        return await self._rows_to_tasks(rows)

    @open_and_close_connection
    async def get_archived_executor(self, executor_id: int, company_code: str, connection=None) -> List[Task]:
        sql_query = (
            f"SELECT * FROM public.task WHERE status IN {tuple(ARCHIVE_TASK_STATUSES)} "
            f"AND company_id = (SELECT company_id FROM public.company WHERE company_code = $1) AND executor_id = $2"
        )
        rows = await connection.fetch(sql_query, company_code, executor_id)
        return await self._rows_to_tasks(rows)

    @open_and_close_connection
    async def get_archived_personal_tasks(self, user_id: int, company_code: str, connection=None) -> List[Task]:
        sql_query = (
            f"SELECT * FROM public.task WHERE status IN {tuple(ARCHIVE_TASK_STATUSES)} "
            f"AND company_id = (SELECT company_id FROM public.company WHERE company_code = $1) "
            f"AND executor_id = $2 AND executor_id = author_id"
        )
        rows = await connection.fetch(sql_query, company_code, user_id)
        return await self._rows_to_tasks(rows)

    @open_and_close_connection
    async def delete(self, task_id: int, connection=None) -> None:
        await connection.fetch(f"DELETE FROM public.task WHERE task_id = $1", task_id)

    @open_and_close_connection
    async def set_status(self, task_id: int, status: str, connection=None):
        await connection.fetch(f"UPDATE public.task SET status = $1 WHERE task_id = $2", status, task_id)

    @open_and_close_connection
    async def set_description(self, task_id: int, new_description: str, new_task_summary: str = None, new_task_tag: str = None, connection=None):
        query = "UPDATE public.task SET description = $1"
        values = [new_description]

        if new_task_summary:
            query += ", task_summary = $2"
            values.append(new_task_summary)

        if new_task_tag:
            query += ", tag = $3"
            values.append(new_task_tag)

        query += " WHERE task_id = $4"
        values.append(task_id)

        await connection.fetch(query, *values)

    @open_and_close_connection
    async def set_tag(self, task_id: int, tag: str, connection=None):
        await connection.fetch("UPDATE public.task SET tag = $1 WHERE task_id = $2", tag, task_id)

    @open_and_close_connection
    async def set_deadline(self, task_id: int, deadline_datetime: datetime, connection=None):
        await connection.fetch("UPDATE public.task SET deadline_datetime = $1 WHERE task_id = $2", deadline_datetime, task_id)


    async def _row_to_task(self, row) -> Task:
        task = Task(
            task_id=row['task_id'],
            author_id=row['author_id'],
            executor_id=row['executor_id'],
            task=row['description'],
            task_summary=row['task_summary'],
            deadline_datetime=row['deadline_datetime'].replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Moscow')),
            status=row['status'],
            tag=row['tag'],
            created_at=row['created_at'].replace(tzinfo=pytz.utc).astimezone(pytz.timezone('Europe/Moscow')),
        )
        task.author_user = await self.users_repository.get_by_id(row['author_id'])
        task.executor_user = await self.users_repository.get_by_id(row['executor_id'])
        company_code = await self.companies_repository.get_company_code_by_company_id(row['company_id'])
        task.company_code = company_code[0]['company_code']
        return task

    async def _rows_to_tasks(self, rows) -> List[Task]:
        list_of_tasks = []
        for row in rows:
            task = await self._row_to_task(row)
            list_of_tasks.append(task)
        return list_of_tasks
