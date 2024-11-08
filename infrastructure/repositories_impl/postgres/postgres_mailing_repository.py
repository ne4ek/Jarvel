import json
from typing import List
from application.repositories.mailing_repository import MailingRepository
from psycopg2.pool import ThreadedConnectionPool
from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection
from domain.entities.mail import Mail
from icecream import ic


class PostgresMailingRepository(MailingRepository):
    def __init__(self, db_connection_pool: ThreadedConnectionPool):
        self.db_connection_pool = db_connection_pool

    @open_and_close_connection
    def save(self, mail: Mail, conn=None, cursor=None) -> int:
        sql_query = (
            "INSERT INTO mailing (author_id, recipients_ids, topic, body, contact_type, file_attachment, "
            "send_at, unknown_recipients_data) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING mailing_id;")
        ic(mail)
        sql_values = (
            mail.author_id,
            mail.recipients_ids,
            mail.topic,
            mail.body,
            mail.contact_type,
            mail.attachment,
            mail.send_at,
            json.dumps(mail.unknown_recipients_data)
        )
        cursor.execute(sql_query, sql_values)
        mailing_id = cursor.fetchone()[0]
        conn.commit()
        return mailing_id

    @open_and_close_connection
    def get_by_id(self, mailing_id: int, conn=None, cursor=None):
        pass

    @open_and_close_connection
    def get_by_author(self, author_id: int, conn=None, cursor=None) -> List[Mail]:
        cursor.execute(f"SELECT * FROM mailing WHERE author_id = '{author_id}'")
        return [Mail(**item) for item in cursor.fetchall()]

    @open_and_close_connection
    def get_by_recipient_ids(self, recipient_ids: int, conn=None, cursor=None) -> List[Mail]:
        cursor.execute(f"SELECT * FROM mailing WHERE recipient_ids = '{recipient_ids}';")
        rows = cursor.fetchall()
        return [Mail(**row) for row in rows]

    @open_and_close_connection
    def get_by_mailing_id(self, mailing_id: int, conn=None, cursor=None) -> Mail:
        cursor.execute = (f'SELECT * FROM mailing WHERE mailing_id = {mailing_id}')
        mail = cursor.fetchall()
        return Mail(**mail)

    @open_and_close_connection
    def get_all(self, conn=None, cursor=None) -> List[Mail]:
        cursor.execute("SELECT * FROM mailing")
        rows = cursor.fetchall()
        return [Mail(*row) for row in rows]

    @open_and_close_connection
    def delete(self, mailing_id: int, conn=None, cursor=None) -> None:
        cursor.execute(f"DELETE FROM mailing WHERE mailing_id = {mailing_id};")
        conn.commit()