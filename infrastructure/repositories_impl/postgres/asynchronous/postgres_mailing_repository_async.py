import json
from typing import List, Optional
from asyncpg.pool import Pool
from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
from domain.entities.mail import Mail
from datetime import datetime
from application.repositories.mailing_repository import MailingRepository
from icecream import ic

class PostgresMailingRepositoryAsync(MailingRepository):
    def __init__(self, db_connection_pool: Pool):
        self.db_connection_pool = db_connection_pool

    @open_and_close_connection
    async def save(self, mail: Mail, connection=None) -> int:
        sql_query = (
            "INSERT INTO public.mail (author_id, known_recipients_ids, topic, body, contact_type, attachment, "
            "send_at, unknown_recipients_data, company_code) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) RETURNING mail_id;"
        )
        sql_values = (
            mail.author_id,
            mail.recipients_ids,
            mail.topic,
            mail.body,
            mail.contact_type,
            mail.attachment,
            mail.send_at,
            json.dumps(mail.unknown_recipients_data),
            mail.company_code
        )
        result = await connection.fetch(sql_query, *sql_values)
        return result[0]["mail_id"]
    @open_and_close_connection
    async def get_by_id(self, mailing_id: int, connection=None) -> Optional[Mail]:
        query = f"SELECT * FROM public.mail WHERE mail_id = {mailing_id}"
        result = await connection.fetch(query)
        return self._map_to_mail(result[0]) if result else None

    @open_and_close_connection
    async def get_by_author(self, author_id: int, connection=None) -> List[Mail]:
        query = f"SELECT * FROM public.mail WHERE author_id = {author_id}"
        result = await connection.fetch(query)
        return [self._map_to_mail(row) for row in result]

    @open_and_close_connection
    async def get_by_recipient_ids(self, recipient_ids: int, connection=None) -> List[Mail]:
        query = f"SELECT * FROM public.mail WHERE {recipient_ids} = ANY(known_recipients_ids);"
        result = await connection.fetch(query)
        return [self._map_to_mail(row) for row in result]

    @open_and_close_connection
    async def get_by_mailing_id(self, mailing_id: int, connection=None) -> Optional[Mail]:
        query = f"SELECT * FROM public.mail WHERE mail_id = {mailing_id}"
        result = await connection.fetch(query)
        return self._map_to_mail(result[0]) if result else None

    @open_and_close_connection
    async def get_all(self, connection=None) -> List[Mail]:
        query = "SELECT * FROM public.mail"
        result = await connection.fetch(query)
        return [self._map_to_mail(row) for row in result]

    @open_and_close_connection
    async def delete(self, mailing_id: int, connection=None) -> None:
        query = f"DELETE FROM public.mail WHERE mail_id = {mailing_id};"
        await connection.fetch(query)

    def _map_to_mail(self, row) -> Mail:
        ic(row)
        return Mail(
            mailing_id=row['mail_id'],
            author_id=row['author_id'],
            recipients_ids=row['known_recipients_ids'],
            topic=row['topic'],
            body=row['body'],
            contact_type=row['contact_type'],
            attachment=row['attachment'],
            send_delay=row.get('send_delay'),
            created_at=row.get('created_at'),
            send_at=row.get('send_at'),
            unknown_recipients_data=json.loads(row['unknown_recipients_data']) if row['unknown_recipients_data'] else [],
            company_code=row.get('company_code')
        )
