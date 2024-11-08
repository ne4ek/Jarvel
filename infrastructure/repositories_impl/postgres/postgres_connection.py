from infrastructure.config.postgres_config import connection_pool
from icecream import ic

def get_connection() -> tuple:
    """
    Get the connection from the connection pool of the database

    :return: A tuple containing connection and cursor
    :rtype: tuple(psycopg2.extensions.connection, psycopg2.extensions.cursor)
    """
    connection = connection_pool.getconn()
    cursor = connection.cursor()

    return connection, cursor



def close_connection(connection, cursor):
    """
    Сlose the database connection

    :param psycopg2.extensions.connection connection:
    :param psycopg2.extensions.cursor cursor:

    :return: None
    """
    cursor.close()
    connection_pool.putconn(connection)


def close_all_connections():
    """
    Close all the database connections

    :return: None
    """
    connection_pool.closeall()


def open_and_close_connection(func):
    """
    The function open connection with database, calls the function, then closes the connection

    :param function func:

    :return: A wrapper over the original function that adds logging before and after the call.
    :rtype: Callable
    """

    # the decorator in which to wrap the functions of working with the database
    def wrapper(*args, **kwargs):
        connection, cursor = get_connection()
        try:
            kwargs['conn'] = connection
            kwargs['cursor'] = cursor
            result = func(*args, **kwargs)
            return result
        finally:
            close_connection(connection, cursor)

    return wrapper


def reform_ro_dictionary(cur):
    """Функция преобразует данные из бд в список, в котором хранятся словари с названиями столбцов и значениями"""
    column_names = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    result = [dict(zip(column_names, row)) for row in rows]
    return result
