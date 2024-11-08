from icecream import ic
from aiogram.types import Message
from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection, \
    reform_ro_dictionary
import pytz
from datetime import datetime


@open_and_close_connection
def save_meetings(args, conn=None, cursor=None):
    """
    Функция сохраняет данные о встрече
    :param dict args: Словарь с данными о встрече
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: None
    """
    cursor.execute("INSERT INTO meetings (moderator_id, participants_id, topic, link, meeting_time, invitation_type,"
                "remind_time, duration) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING meeting_id;",
                (args.get('moderator'), args.get('known_participants'), args.get('topic'),
                 args.get('link'), args.get('meeting_time_datetime_format'), args.get('invitation_type'),
                 args.get('remind_time_datetime_format'),
                 args.get('duration')))

    conn.commit()
    meeting_id = cursor.fetchone()[0]
    # ic(meeting_id)
    return meeting_id


@open_and_close_connection
def get_all_from_meetings(conn=None, cursor=None):
    """
    Функция возвращает всю информацию о всех созвонах
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: Словарь всех данных
    """
    cursor.execute("SELECT * FROM meetings;")
    column_names = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    result = [dict(zip(column_names, row)) for row in rows]
    return result


@open_and_close_connection
def get_all_from_meetings_by_user(user_id: int, conn=None, cursor=None):
    """
    Функция возвращает все встречи где участник является модератором или участником

    :param int user_id: ID пользователя
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return list: Список словарей все встреч
    """

    cursor.execute(f"SELECT * FROM meetings WHERE moderator_id = '{user_id}' OR {user_id} = ANY(participants_id)")
    return reform_ro_dictionary(cursor)


@open_and_close_connection
def get_last_n_meetings_by_user(user_id: int, n: int, conn=None, cursor=None):
    """
    Функция возвращает n встреч где участник является модератором или участником

    :param int user_id: ID пользователя
    :param int n: Количество встреч
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return list: Список словарей все встреч
    """
    ic(user_id)
    cursor.execute(f"SELECT * FROM meetings "
                f"WHERE moderator_id = '{user_id}' OR {user_id} = ANY(participants_id) "
                f"ORDER BY meeting_time ASC LIMIT {n} ")
    return reform_ro_dictionary(cursor)


@open_and_close_connection
def get_all_from_meetings_by_user_filter_datetime(user_id: int, deadline_days: str, deadline_time: str, conn=None, cursor=None):
    """
    Функция возвращает все встречи где участник является модератором или участником

    :param int user_id: ID пользователя
    :param str deadline_days: День до которого надо найти все встречи. Формат: только число дней
    :param str deadline_time: Время до которого надо найти все встречи. Формат: 'HH:MM'
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return list: Список словарей все встреч
    """

    sql_request = f"SELECT * FROM meetings WHERE (moderator_id = '{user_id}' OR {user_id} = ANY(participants_id)) "

    datetime_sql_part = ("AND meeting_time AT TIME ZONE 'Europe/Moscow' <= "
                         "DATE_TRUNC('day', NOW()) + "
                         "INTERVAL '{} days' + INTERVAL '{} hour' + INTERVAL '{} minutes' ").format(
        deadline_days,
        deadline_time.split(':')[0],
        deadline_time.split(':')[1]
    )
    sql_request += datetime_sql_part
    sql_request += "ORDER BY meeting_time ASC"
    cursor.execute(sql_request)
    return reform_ro_dictionary(cursor)


@open_and_close_connection
def get_all_about_meeting(meeting_id: int, conn=None, cursor=None):
    """
    Функция возвращает n встреч где участник является модератором или участником

    :param int meeting_id: ID встречи
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return list: Словарь со всеми данными о встрече
    """

    cursor.execute(f"SELECT * FROM meetings WHERE meeting_id = '{meeting_id}'")
    return reform_ro_dictionary(cursor)[0]





# ic| data: {'invitation_type': 'telegram',
#            'known_participants': [603789543, 6016855180],
#            'link': 'yandex.ru',
#            'meeting_date': '15.05.2024',
#            'meeting_time': '18:23',
#            'moderator': 491949946331,
#            'remind_date': '15.05.2024',
#            'remind_time': '14:23',
#            'topic': 'битва с джокером и стратегия победы над ним',
#            'unknown_participants': []}
