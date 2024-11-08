# import psycopg2
# from psycopg2 import pool
# import os
# from typing import Any
# from icecream import ic
# from dotenv import load_dotenv
#
# load_dotenv()
# conn: Any = None
# cur: Any = None
# connection_pool = pool.ThreadedConnectionPool(
#     1,
#     20,
#     user=os.getenv("DB_USER"),
#     password=os.getenv("DB_PASSWORD"),
#     host=os.getenv("DB_HOST"),
#     port=os.getenv("DB_PORT"),
#     database=os.getenv("DB_NAME"),
#     keepalives=1,
#     keepalives_idle=60,
#     keepalives_interval=15,
#     keepalives_count=10
# )
#
#
# def execute(command) -> None:
#     """
#     Execute the command to do something with the database
#
#     :param str command:
#
#     :return: None
#     """
#     cur.execute(command)
#     conn.commit()
#
#
# def get_data(command) -> tuple:
#     """
#     Execute the command from the database that returns a data
#
#     :param str command:
#
#     :return: The data from the database
#     :rtype: tuple
#     """
#     cur.execute(command)
#     data = cur.fetchall()
#     return data
#
#
# def get_connection() -> tuple:
#     """
#     Get the connection from the connection pool of the database
#
#     :return: A tuple containing connection and cursor
#     :rtype: tuple(psycopg2.extensions.connection, psycopg2.extensions.cursor)
#     """
#     connection = connection_pool.getconn()
#     cursor = connection.cursor()
#
#     return connection, cursor
#
#
# def close_connection(connection, cursor):
#     """
#     Сlose the database connection
#
#     :param psycopg2.extensions.connection connection:
#     :param psycopg2.extensions.cursor cursor:
#
#     :return: None
#     """
#     cursor.close()
#     connection_pool.putconn(connection)
#
#
# def close_all_connections():
#     """
#     Close all the database connections
#
#     :return: None
#     """
#     connection_pool.closeall()
#
#
# def open_and_close_connection(func):
#     """
#     The function open connection with database, calls the function, then closes the connection
#
#     :param function func:
#
#     :return: A wrapper over the original function that adds logging before and after the call.
#     :rtype: Callable
#     """
#
#     # the decorator in which to wrap the functions of working with the database
#     def wrapper(*args, **kwargs):
#         connection, cursor = get_connection()
#         try:
#             result = func(conn=connection, cur=cursor, *args, **kwargs)
#             return result
#         finally:
#             close_connection(connection, cursor)
#
#     return wrapper
#
#
# def reform_ro_dictionary(cur):
#     """Функция преобразует данные из бд в список, в котором хранятся словари с названиями столбцов и значениями"""
#     column_names = [desc[0] for desc in cur.description]
#     rows = cur.fetchall()
#     result = [dict(zip(column_names, row)) for row in rows]
#     return result
