from datetime import datetime
from icecream import ic
from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection


@open_and_close_connection
def save_task(data: dict, conn=None, cursor=None):
    """
    Saves a task into the database.

    :param data: Dictionary containing task data.
    :type data: dict
    :param conn: PostgreSQL database connection.
    :type conn: psycopg2.extensions.connection
    :param cursor: PostgreSQL database cursorsor.
    :type cursor: psycopg2.extensions.cursorsor
    :return: ID of the newly saved task.
    :rtype: int
    """
    cursor.execute(
        "INSERT INTO tasks (author_id, executor_id, task, deadline, task_summary, status, tag) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING task_id;",
        (
            int(data.get("task_author_id")),
            int(data.get("executor_id")),
            data.get("task"),
            data.get("deadline"),
            data.get("task_summary"),
            "active",
            data.get("tag"),
        ),
    )
    new_id = cursor.fetchone()[0]
    conn.commit()
    return new_id


@open_and_close_connection
def get_all_from_tasks_by_user(executor_id: int = None, author_id: int = None,
                               status: str = None, additional_filters: dict = None,
                               conn=None, cursor=None):
    """
    Retrieves all tasks assigned to a specific executor with a given status.

    :param int executor_id: ID of the executor.
    :param int author_id: ID of the author.
    :param str status: Status of the tasks to retrieve.
    :param dict additional_filters: {'tag': str, 'deadline_days': str, 'deadline_time': str(HH:MM)}
    :param psycopg2.extensions.connection conn: PostgreSQL database connection.
    :param psycopg2.extensions.cursorsor cursor: PostgreSQL database cursorsor.

    :return dict: Dictionary of tasks with column_namen.
    """
    type_of_user = None
    user_id = None
    if executor_id is not None and author_id is None:
        type_of_user = "executor_id"
        user_id = executor_id
    elif executor_id is None and author_id is not None:
        type_of_user = "author_id"
        user_id = author_id

    sql_request = f"SELECT * FROM tasks WHERE {type_of_user} = '{user_id}' AND status = '{status}' "

    if additional_filters is not None:
        # sql_request = f"-- SELECT * FROM tasks WHERE {type_of_user} = '{user_id}' AND status = '{status}' "

        # Добавление условие на теги
        if additional_filters.get('tag') is not None:
            sql_request += f"AND tag = '{additional_filters.get('tag')}' "

        # Добавление условие на дедлайн
        if additional_filters.get('deadline_days') is not None:
            datetime_sql_part = ("AND deadline AT TIME ZONE 'Europe/Moscow' <= "
                                 "DATE_TRUNC('day', NOW()) + "
                                 "INTERVAL '{} days' + INTERVAL '{} hour' + INTERVAL '{} minutes'").format(
                additional_filters.get('deadline_days'),
                additional_filters.get('deadline_time').split(':')[0],
                additional_filters.get('deadline_time').split(':')[1]
            )

            sql_request += datetime_sql_part

    sql_request += "ORDER BY deadline ASC"
    cursor.execute(sql_request)

    column_names = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    result = [dict(zip(column_names, row)) for row in rows]
    return result



# @open_and_close_connection
# def get_all_from_authors_tasks(author_id: int, status: str, additional_filters: dict = None, conn=None, cursor=None):
#     """
#     Retrieves all tasks assigned to a specific author with a given status.
#
#     :param int author_id: ID of the author.
#     :param str status: Status of the tasks to retrieve.
#     :param dict additional_filters: Словарь дополнительных фильтров
#     :param psycopg2.extensions.connection conn: PostgreSQL database connection.
#     :param psycopg2.extensions.cursorsor cursor: PostgreSQL database cursorsor.
#     :return: List of tasks.
#     :rtype: list
#     """
#     cursor.execute(
#         f"SELECT * FROM tasks WHERE author_id = '{author_id}' AND status = '{status}';"
#     )
#     data = cursor.fetchall()
#     return data


@open_and_close_connection
def get_task_from_tasks(task_id: int, conn=None, cursor=None):
    """
    Retrieves a task from the database by its ID.

    :param task_id: ID of the task.
    :type task_id: int
    :param conn: PostgreSQL database connection.
    :type conn: psycopg2.extensions.connection
    :param cursor: PostgreSQL database cursorsor.
    :type cursor: psycopg2.extensions.cursorsor
    :return: Task data.
    :rtype: tuple
    """
    cursor.execute(f"SELECT * FROM tasks WHERE task_id = '{task_id}';")
    data = cursor.fetchone()
    return data


@open_and_close_connection
def set_task_status(task_id: int, status: str, conn=None, cursor=None):
    """
    Updates the status of a task in the database.

    :param task_id: ID of the task.
    :type task_id: int
    :param status: New status of the task.
    :type status: str
    :param conn: PostgreSQL database connection.
    :type conn: psycopg2.extensions.connection
    :param cursor: PostgreSQL database cursorsor.
    :type cursor: psycopg2.extensions.cursorsor
    """
    cursor.execute(f"UPDATE tasks SET status = '{status}' WHERE task_id = '{task_id}';")
    conn.commit()
    # data = cursor.fetchone()
    # return data
