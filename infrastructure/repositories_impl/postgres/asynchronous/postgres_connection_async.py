from infrastructure.config.postgres_config_async import get_connection_pool
import logging
import asyncpg
from icecream import ic

async def get_connection():
    connection = await get_connection_pool().acquire()

    return connection


async def release_connection(connection):
    await get_connection_pool().release(connection)
    

async def close_all_connections():
    await get_connection_pool().close()


def open_and_close_connection(func):
    # the decorator in which to wrap the functions of working with the database
    async def wrapper(*args, **kwargs):
        connection = await get_connection()
        try:
            kwargs['connection'] = connection
            result = await func(*args, **kwargs)
            return result
        except asyncpg.exceptions._base.InterfaceError as e:
            logging.error(f"InterfaceError in function {func.__name__}: {e}")
            raise
        except Exception as e:
            logging.error(f"Error in function {func.__name__}: {e}")
            raise
        finally:
            await release_connection(connection)

    return wrapper


def reform_ro_dictionary(cur):
    """Функция преобразует данные из бд в список, в котором хранятся словари с названиями столбцов и значениями"""
    column_names = [desc[0] for desc in cur.description]
    rows = cur.fetchall()
    result = [dict(zip(column_names, row)) for row in rows]
    return result
