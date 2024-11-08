from datetime import datetime
from icecream import ic

from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection
# from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection


@open_and_close_connection
def create_company(data, conn=None, cursor=None) -> None:
    """
    Create a new company

    :param dict data: Data to create company {'code': str,'company_name': str, 'description': str, 'owner_id': str }
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: None
    """
    cursor.execute(
        "INSERT INTO companies (code, name, description, owner_id) "
        "VALUES (%s, %s, %s, %s);",
        (data["code"], data["company_name"], data["description"], data["owner_id"]),
    )
    conn.commit()

    add_user_id_in_company(user_id=data['owner_id'], company_code=data['code'])


@open_and_close_connection
def get_code_from_companies(conn=None, cursor=None):
    """
    Return all company codes

    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: Company of the code
    :rtype: tuple
    """
    cursor.execute("SELECT company_code FROM company;")
    data = [item[0] for item in cursor.fetchall()]
    return data


@open_and_close_connection
def is_company_code_exists(company_code: str, conn=None, cursor=None):
    """
    Check if company code exists

    :param str company_code: Company code
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: Company of the code
    :rtype: tuple
    """

    cursor.execute(f"SELECT EXISTS(SELECT code from companies WHERE code = '{company_code}');")
    data = cursor.fetchone()[0]
    # ic(data)
    return data


@open_and_close_connection
def get_code_owner_from_companies(conn=None, cursor=None):
    """
    Return company codes and owner ids from all companies

    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: Codes of the companies and owners id
    :rtype: tuple
    """
    cursor.execute("SELECT code, owner_id FROM companies;")
    data = cursor.fetchall()
    return data


@open_and_close_connection
def get_code_owner_from_company(company_code: str, conn=None, cursor=None):
    """
    Return code owner from company by company code

    :param str company_code: The code of the company you are looking for
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: Company code and owner_id
    :rtype: tuple
    """
    cursor.execute(f"SELECT company_code, owner_id FROM company WHERE company_code = '{company_code}';")
    data = cursor.fetchone()
    return data


@open_and_close_connection
def get_users_id_from_company(company_code: str, conn=None, cursor=None):
    """
    Return all users id from company by company code

    :param str company_code: The code of the company you are looking for
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: Tuple of users id
    :rtype: tuple
    """
    cursor.execute(f"SELECT users_id FROM companies WHERE code = '{company_code}'")
    data = [item[0] for item in cursor.fetchall()]
    return data


@open_and_close_connection
def get_company_code_from_group_chat(chat_id: int, conn=None, cursor=None):
    """
    Return company code from group chat by group chat id

    :param int chat_id: Group chat id
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: Company code
    :rtype: str
    """
    cursor.execute(f"SELECT company_code from group_chats where chat_id = '{chat_id}'")
    data = cursor.fetchone()[0]
    return data


@open_and_close_connection
def get_chat_id_from_group_chats(conn=None, cursor=None):
    """
    Return chat id from all group chats

    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: Tuple of chat id
    :rtype: tuple
    """
    cursor.execute("SELECT chat_id from group_chats;")
    data = [item[0] for item in cursor.fetchall()]
    return data


@open_and_close_connection
def get_owner_id_from_company(company_code, conn=None, cursor=None):
    """
    Return owner id from company by company code

    :param str company_code: The code of the company you are looking for
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: Owner id from company
    :rtype: str
    """
    cursor.execute(f"SELECT owner_id FROM companies WHERE code='{company_code}'")
    data = cursor.fetchone()[0]
    return data


@open_and_close_connection
def add_users_chat_in_company(
        chat_id: int, role: str, company_code: str, conn=None, cursor=None
):
    """
    Save a new users chat in company

    :param int chat_id: Chat id of the user
    :param str role: The role of the user in company
    :param str company_code: The code of the company to add the data to
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: None
    """
    cursor.execute(
        "INSERT INTO user_chats (chat_id, role, company_code) VALUES (%s, %s, %s);",
        (chat_id, role, company_code),
    )
    conn.commit()


@open_and_close_connection
def add_groups_chat_in_company(
        chat_id: int, name: str, company_code: str, owner_id: int, conn=None, cursor=None
):
    """
    Save a new group chat in company

    :param type chat_id: The group chat id
    :param type name: The name of the group chat
    :param type company_code: The code of company to add the data to
    :param type owner_id: The owner of the company
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return:
    :rtype:
    """
    cursor.execute(
        "INSERT INTO group_chats (chat_id, name, company_code, owner_id) "
        "VALUES (%s, %s, %s, %s);",
        (chat_id, name, company_code, owner_id),
    )
    conn.commit()


@open_and_close_connection
def add_user_id_in_company(user_id: int, company_code: str, conn=None, cursor=None):
    """
    Save user id in company by company code

    :param int user_id: Chat id of the user
    :param str company_code: The code of the company to add the data to
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: None
    """
    cursor.execute(
        f"UPDATE companies SET users_id = users_id || {user_id} where code = '{company_code}'"
    )
    conn.commit()


@open_and_close_connection
def is_user_in_chat_registered(chat_id, role, company_code, conn=None, cursor=None):
    """
    The function check if the user in chat in database

    :param int chat_id: The chat id from user
    :param str role: The role that the user sent
    :param str company_code: The code of the company the user wants to join
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator


    :return: boolean value is there a user in the database
    :rtype: bool
    """
    cursor.execute(
        f"SELECT EXISTS(SELECT 1 FROM user_chats WHERE chat_id = '{chat_id}' AND company_code = '{company_code}' "
        f"AND role = '{role}')"
    )
    data = cursor.fetchone()[0]
    return data


@open_and_close_connection
def is_group_in_company_registered(
        chat_id: int, company_code: str, conn=None, cursor=None
):
    """
    Return boolean answer is this group in company registered

    :param int chat_id: The id of the group
    :param str company_code: the code of the company in which to check the registration of the group
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: Is this group registered with the company
    :rtype: bool
    """
    cursor.execute(
        f"SELECT EXISTS(SELECT 1 FROM group_chat WHERE group_chat_id = '{chat_id}' AND company_id = '{company_code}')"
    )

    data = cursor.fetchone()[0]
    return data


@open_and_close_connection
def get_company_name_from_company(company_code: str, conn=None, cursor=None):
    """
    Return company_name from company
    :param str company_code: the code of the company

    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return str: Company of the code
    """
    cursor.execute(f"SELECT name FROM companies WHERE code='{company_code}';")
    data = cursor.fetchone()[0]
    return data


@open_and_close_connection
def get_all_companies_names_from_company_by_user(user_id: int, conn=None, cursor=None):
    """
    Return companies_names in which user exists
    :param int user_id: the code of the company

    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return str: Company of the code
    """
    cursor.execute(f"SELECT name FROM companies WHERE '{user_id}' = ANY (users_id);")
    data = [name[0] for name in cursor.fetchall()]
    return data


@open_and_close_connection
def get_all_companies_names_where_user_owner(user_id: int, conn=None, cursor=None):
    """
    Return companies_names in which user exists
    :param int user_id: the code of the company

    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return str: Company of the code
    """
    cursor.execute(f"SELECT name FROM companies WHERE owner_id = '{user_id}';")
    data = [name[0] for name in cursor.fetchall()]
    return data


@open_and_close_connection
def get_owner_company_name_by_company_code(company_code: str, conn=None, cursor=None):
    """
    Функция возвращает имя владельца
    """
    cursor.execute("SELECT u.name "
                "FROM companies c "
                "JOIN users u ON c.owner_id = u.user_id "
                f"WHERE code = '{company_code}';")
    # cursor.execute(f"SELECT name FROM companies WHERE code = '{company_code}';")
    data = cursor.fetchone()[0]
    return data


@open_and_close_connection
def get_description_from_company(company_code: str, conn=None, cursor=None):
    """
    Функция возвращает описание компании
    """
    cursor.execute(f"SELECT name FROM companies WHERE code = '{company_code}';")
    data = cursor.fetchone()[0]
    return data


@open_and_close_connection
def get_participants_names_from_company_by_company_code(company_code: str, conn=None, cursor=None):
    "Функция возвращает список имён пользователей, которые состоят в компании"
    cursor.execute(
        "SELECT string_agg(u.name, ', ') AS user_names "
        "FROM companies c "
        "JOIN LATERAL unnest(c.users_id) AS uid(user_id) ON true "
        "JOIN users u ON u.user_id = uid.user_id "
        f"WHERE c.code = '{company_code}';")

    return cursor.fetchone()[0]