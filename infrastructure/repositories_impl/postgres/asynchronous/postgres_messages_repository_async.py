from domain.entities.message import Message
from application.repositories.messages_repository import MessagesRepository
from application.repositories.users_repository import UsersRepository
from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection
from typing import List
import pytz
from icecream import ic


class PostgresMessagesRepositoryAsync(MessagesRepository):
    def __init__(self, db_connection_pool, users_repository: UsersRepository):
        self.db_connection_pool = db_connection_pool
        self.users_repository: UsersRepository = users_repository

    @open_and_close_connection
    async def save(self, message: Message, connection=None):
        count_of_messages = await self.get_count_messages_by_chat_id(message.chat_id)
        if count_of_messages >= 50:
            await connection.execute("""
            DELETE FROM public.message 
            WHERE message_id = (
                SELECT message_id 
                FROM public.message
                WHERE chat_id = $1
                ORDER BY message_id 
                LIMIT 1
            )
            """,
            message.chat_id
            )

        await connection.execute(
            "INSERT INTO public.message (message_id, user_id, text, date, replied_message_id, chat_id) VALUES ($1, $2, $3, $4, $5, $6);",
            message.message_id,
            message.author_id,
            message.text,
            message.date,
            message.replied_message_id,
            message.chat_id
        )

    @open_and_close_connection
    async def get_count_messages_by_chat_id(self, chat_id: int, connection=None):
        result = await connection.fetch(
            """
            SELECT COUNT(*)
            FROM public.message
            JOIN public.group_chat ON public.message.chat_id = public.group_chat.group_chat_id
            WHERE public.message.chat_id = $1
            """,
            chat_id
        )
        return result[0]['count']

    @open_and_close_connection
    async def get_n_last_messages_by_chat_id(self, chat_id: int, bot_id: int, n: int, connection=None) -> List[Message]:
        query =  f"""
            SELECT * FROM public.message
            WHERE chat_id = {chat_id}
            ORDER BY message_id DESC 
            LIMIT {n};
            """
        result = await connection.fetch(
            query
        )
        data = result
        users = {}
        result = []
        for row in data:
            msg = Message()
            # ic(row)
            msg.message_id = row['message_id']
            msg.chat_message_id = row['message_id']
            if row['user_id'] == bot_id:
                msg.is_bot_message = True
            elif row['user_id'] not in users:
                msg.is_bot_message = False
                users[row['user_id']] = await self.users_repository.get_by_id(row['user_id'])
            msg.author_id = row['user_id']
            if not msg.is_bot_message:
                msg.author_user = users[row['user_id']]
            msg.text = row['text']
            msg.date = row['date'].astimezone(pytz.timezone("Europe/Moscow"))
            msg.replied_message_id = row['replied_message_id']
            result.append(msg)
        return result
