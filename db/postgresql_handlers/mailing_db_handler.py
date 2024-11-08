from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection


@open_and_close_connection
def save_mailing(args, conn=None, cursor=None):
    """
    Функция сохраняет данные о рыссылке
    :param dict args: Словарь с данными о рассылке
    :param psycopg2.extensions.connection conn: The value automatically injected by the decorator
    :param psycopg2.extensions.cursorsor cursor: The value automatically injected by the decorator

    :return: id созданной рассылки
    """
    cursor.execute(
        "INSERT INTO mailing (author_id, recipients_ids, topic, body, contact_type, attachment)"
        "VALUES (%s, %s, %s, %s, %s, %s) RETURNING mailing_id;",
        (args.get("mailing_autor_id"),
         args.get("recipients_ids"),
         args.get("topic"),
         args.get("body"),
         args.get("contact_type"),
         args.get("attachment")))
    conn.commit()

    mail_id = cursor.fetchone()[0]
    return mail_id

@open_and_close_connection
def get_all_from_meetings(conn=None, cursor=None):
    """
    Функция возвращает всю информацию о всех созвонах
    :return: Словарь всех данных
    """
    cursor.execute("SELECT * FROM mailing;")
    column_names = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    result = [dict(zip(column_names, row)) for row in rows]
    return result