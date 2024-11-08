from datetime import datetime
from icecream import ic
from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection


@open_and_close_connection
def user_is_exists(user_id: int, conn=None, cursor=None):
    """
    Checks if a user with the given user_id exists in the database.

    :param int user_id: ID of the user.
    :param psycopg2.extensions.connection conn: PostgreSQL database connection.
    :param psycopg2.extensions.cursorsor cursor: PostgreSQL database cursorsor.

    :return: True if the user exists, False otherwise.
    :rtype: bool
    """
    cursor.execute(f"SELECT EXISTS(SELECT 1 FROM public.user WHERE user_id = '{user_id}')")
    data = cursor.fetchone()[0]

    return data


@open_and_close_connection
def get_all_about_users_from_company(company_code, conn=None, cursor=None):
    """
    Retrieves all user data associated with the given company code.

    :param str company_code: Code of the company.
    :param psycopg2.extensions.connection conn: PostgreSQL database connection.
    :param psycopg2.extensions.cursorsor cursor: PostgreSQL database cursorsor.
    :return: List of user data.
    :rtype: list
    """
    cursor.execute(f"""
    SELECT * FROM users
    JOIN companies ON users.user_id = ANY(companies.users_id)
    WHERE companies.code = '{company_code}';
    """)
    data = cursor.fetchall()
    return data


@open_and_close_connection
def get_all_about_owner_from_company(company_code, conn=None, cursor=None):
    """
    Retrieves all owner data associated with the given company code.

    :param str company_code: Code of the company.
    :param psycopg2.extensions.connection conn: PostgreSQL database connection.
    :param psycopg2.extensions.cursorsor cursor: PostgreSQL database cursorsor.
    :return: List of user data.
    :rtype: list
    """
    cursor.execute(f"""
    SELECT * FROM users
    JOIN companies ON users.user_id = companies.owner_id
    WHERE companies.code = '{company_code}';
    """)
    data = cursor.fetchall()[0]
    return data


@open_and_close_connection
def get_users_usernames_from_companies(chat_id, conn=None, cursor=None):
    """
    Retrieves the usernames of users associated with the given chat ID.

    :param int chat_id: ID of the chat.
    :param psycopg2.extensions.connection conn: PostgreSQL database connection.
    :param psycopg2.extensions.cursorsor cursor: PostgreSQL database cursorsor.
    :return: List of usernames.
    :rtype: list
    """
    cursor.execute(
        f"""
    SELECT users.username
    FROM companies
             JOIN group_chats ON companies.code = group_chats.company_code

             JOIN LATERAL unnest(companies.users_id) AS uid ON true

             JOIN users ON users.user_id = uid

    WHERE group_chats.chat_id = '{chat_id}'
    """
    )

    usernames = [item[0] for item in cursor.fetchall()]
    return usernames


@open_and_close_connection
def get_owner_id_from_companies(chat_id, conn=None, cursor=None):
    """
    Retrieves the owner ID of the company associated with the given chat ID.

    :param int chat_id: ID of the chat.
    :param psycopg2.extensions.connection conn: PostgreSQL database connection.
    :param psycopg2.extensions.cursorsor cursor: PostgreSQL database cursorsor.
    :return: Owner ID of the company.
    :rtype: int
    """

    cursor.execute(
        f"""SELECT companies.owner_id FROM companies
         JOIN group_chats ON companies.code = group_chats.company_code

--     	JOIN LATERAL unnest(companies.users_id) AS uid ON true

--     	 JOIN users ON users.user_id = uid

        WHERE group_chats.chat_id = '{chat_id}'"""
    )

    data = cursor.fetchone()[0]
    # ic(data)
    return data


@open_and_close_connection
def get_name_from_user(user_id, conn=None, cursor=None):
    """
    Функция возвращает имя пользователя по user_id

    :param int user_id: ID of the user.
    :param psycopg2.extensions.connection conn: PostgreSQL database connection.
    :param psycopg2.extensions.cursorsor cursor: PostgreSQL database cursorsor.
    :return str: User name.
    """
    cursor.execute("SELECT name FROM users WHERE user_id = '{}'".format(user_id))
    date = cursor.fetchone()[0]
    return date


@open_and_close_connection
def get_all_companies_from_user(user_id, conn=None, cursor=None):
    """
    Функция возвращает список компаний в которых пользователь состоит по user_id

    :param int user_id: ID of the user.
    :param psycopg2.extensions.connection conn: PostgreSQL database connection.
    :param psycopg2.extensions.cursorsor cursor: PostgreSQL database cursorsor.
    :return list[str]: Companies codes list.
    """

    cursor.execute(f"SELECT company_code FROM user_chats WHERE chat_id='{user_id}'")
    data = [item[0] for item in cursor.fetchall()]
    return data


@open_and_close_connection
def save_personal_link(user_id: int, personal_link: str, conn=None, cursor=None):
    """
    Saves users personal link into the database.

    :param user_id: ID of the user
    :param personal_link: Personal link of the user
    :param psycopg2.extensions.connection conn: PostgreSQL database connection.
    :param psycopg2.extensions.cursorsor cursor: PostgreSQL database cursorsor.
    """
    cursor.execute(f"UPDATE users SET personal_link = '{personal_link}' WHERE user_id = {user_id}")
    conn.commit()


@open_and_close_connection
def save_email(user_id: int, email: str, conn=None, cursor=None):
    """
    Saves users personal link into the database.

    :param int user_id: ID of the user
    :param str email: Email of the user
    :param psycopg2.extensions.connection conn: PostgreSQL database connection.
    :param psycopg2.extensions.cursorsor cursor: PostgreSQL database cursorsor.
    """
    cursor.execute(f"UPDATE users SET email = '{email}' WHERE user_id = {user_id}")
    conn.commit()



