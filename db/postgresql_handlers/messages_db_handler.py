from icecream import ic
from aiogram.types import Message

from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection


@open_and_close_connection
def save_message(message: Message, company_code="-", text=None, conn=None, cursor=None):
    """
    Save a message from chat

    :param Message message: The message that will be saved
    :param str company_code: The code of the company in which the message was written
    :param str text: The text of the message
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: None
    """
    count_of_messages = get_count_messages_in_chat_by_company_code(company_code)
    if count_of_messages >= 50:
        cursor.execute(f"DELETE FROM messages WHERE chat_message_id = "
                    f"(SELECT chat_message_id from messages "
                    f"where company_code = '{company_code}' ORDER BY chat_message_id LIMIT 1)")
        conn.commit()

    if text is None:
        text = message.text

    cursor.execute(
        "INSERT INTO messages (chat_message_id, author_id, company_code, text, date) VALUES (%s, %s, %s, %s, %s);",
        (
            message.message_id,
            message.from_user.id,
            company_code,
            text,
            message.date,
        ),
    )
    conn.commit()


@open_and_close_connection
def get_count_messages_in_chat_by_company_code(company_code: str, conn=None, cursor=None):
    """
    Функция возвращает количество сообщений в чате
    :param str company_code: The company_code of the chat
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator
    :return int: The count of messages in the chat
    """
    cursor.execute(f"SELECT COUNT(*) FROM messages WHERE company_code = '{company_code}'")
    data = cursor.fetchone()[0]
    return data


@open_and_close_connection
def get_n_last_messages_in_group_chat(chat_id: int, n: int, conn=None, cursor=None):
    """
    Save a message from chat

    :param Message chat_id: ID of the chat from which to retrieve n messages
    :param str n: Number of messages to return
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: Last n messages
    :rtype: list
    """



"""
CREATE TABLE messages (
chat_message_id BIGINT,
author_id BIGINT,
company_code TEXT,
text TEXT,
date TIMESTAMP
);
"""
