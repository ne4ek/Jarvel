from datetime import datetime
from icecream import ic
from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection


@open_and_close_connection
def get_scheduler_jobs(conn=None, cursor=None):
    """
    Return all the scheduler jobs

    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursor cursor: The value automatically injected by the decorator

    :return: Tuple of data about all the scheduler jobs
    :rtype: tuple
    """
    cursor.execute("SELECT * FROM scheduler_jobs")
    data = cursor.fetchall()

    return data


@open_and_close_connection
def save_scheduler_job(type_of_job, trigger, run_date, sender, users_mentioned,
                       reply_message_id, chat_id, conn=None, cursor=None):
    """
    Save a new scheduler job

    :param str type_of_job: Type of job to save
    :param str trigger: Trigger of job
    :param datetime run_date: Date and time of job
    :param str sender: Sender username

    :param users_mentioned: Users to mention
    :type users_mentioned: str, list[str]

    :param int reply_message_id: The ID of the message to reply to
    :param int chat_id: The ID of the chat
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursor cursor: The value automatically injected by the decorator

    :return: None
    """
    # TODO переделать users_mentioned из text на text[]
    if isinstance(users_mentioned, list):
        users_usernames = " ".join(users_mentioned)
    else:
        users_usernames = users_mentioned

    cursor.execute(
        "INSERT INTO scheduler_jobs (job_type, trigger, run_date, sender_username, users_ctrl_usernames, reply_message_id, chat_id) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s);",
        (type_of_job, trigger, run_date, sender, users_usernames, reply_message_id, chat_id),
    )
    conn.commit()


@open_and_close_connection
def save_scheduler_job_without_users_mentioned(type_of_job, trigger, run_date, sender,
                                               reply_message_id, chat_id, conn=None, cursor=None):
    """
    Save a new scheduler job without users to mention


    :param str type_of_job: Type of job to save
    :param str trigger: Trigger of job
    :param datetime run_date: Date and time of job
    :param str sender: Sender username
    :param int reply_message_id: The ID of the message to reply to
    :param int chat_id: The ID of the chat
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursor cursor: The value automatically injected by the decorator

    :return: None
    """
    cursor.execute(
        "INSERT INTO scheduler_jobs (job_type, trigger, run_date, sender_username, reply_message_id, chat_id) "
        "VALUES (%s, %s, %s, %s, %s, %s);",
        (type_of_job, trigger, run_date, sender, reply_message_id, chat_id),
    )
    conn.commit()


@open_and_close_connection
def get_all_from_scheduler_jobs(conn=None, cursor=None):
    """
    Return all information from scheduler jobs

    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursor cursor: The value automatically injected by the decorator

    :return: Tuple(type, trigger, run_date, sender_username, reply_message_id, chat_id)
    :rtype: tuple
    """
    cursor.execute("SELECT job_id, job_type, trigger, run_date, reply_message_id, chat_id, "
                "sender_username, users_ctrl_usernames "
                "FROM scheduler_jobs")

    column_names = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    result = [dict(zip(column_names, row)) for row in rows]

    return result


@open_and_close_connection
def delete_scheduler_job(chat_id: int, message_id: int, conn=None, cur=None):
    """
    Delete scheduler job from the table

    :param int chat_id: Chat id mentioned in the job
    :param int message_id: Message id mentioned in the job
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursor cur: The value automatically injected by the decorator

    :return: None
    """
    cur.execute(
        f"DELETE FROM scheduler_jobs WHERE chat_id = '{chat_id}' AND reply_message_id = '{message_id}'"
    )
    conn.commit()


@open_and_close_connection
def delete_scheduler_job_by_job_id(job_id: int, conn=None, cursor=None):
    """
    Delete scheduler job from the table

    :param int job_id: Job id mentioned in the job
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursor cursor: The value automatically injected by the decorator

    :return: None
    """
    cursor.execute(
        f"DELETE FROM scheduler_jobs WHERE job_id = '{job_id}';"
    )
    conn.commit()





