from datetime import datetime
from icecream import ic
from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection


@open_and_close_connection
def get_group_chat_name(chat_id: int, conn=None, cursor=None) -> None:
    """
    Get name of the group chat

    :param int chat_id: The ID of the chat
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: None
    """
    cursor.execute(f"SELECT name FROM group_chats WHERE chat_id = '{chat_id}'")
    data = cursor.fetchone()[0]
    return data


@open_and_close_connection
def delete_company_from_group_chat(chat_id: int, conn=None, cursor=None) -> None:
    """
    Delete company from group chat

    :param int chat_id: The ID of the chat
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator
    """

    cursor.execute(f"DELETE FROM group_chats WHERE chat_id = '{chat_id}'")
    conn.commit()

@open_and_close_connection
def is_group_chat_in_company(chat_id: int, conn=None, cursor=None) -> bool:
    """
    Check if group chat is in company

    :param int chat_id: The ID of the chat
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return bool: True if group chat is in company
    """
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM group_chat WHERE group_chat_id = '{chat_id}')")
    data = cursor.fetchone()[0]
    return data



