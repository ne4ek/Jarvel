from domain.entities.message import Message
from application.repositories.messages_repository import MessagesRepository
from application.repositories.users_repository import UsersRepository
from psycopg2.pool import ThreadedConnectionPool
from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection
import pytz
from icecream import ic



class PostgresMessagesRepository(MessagesRepository):
    def __init__(self, db_connection_pool: ThreadedConnectionPool, users_repository: UsersRepository):
        self.db_connection_pool = db_connection_pool
        self.users_repository = users_repository

    @open_and_close_connection
    def save(self, message: Message, conn=None, cursor=None):
        count_of_messages = self.get_count_messages_by_chat_id(message.chat_id)
        if count_of_messages >= 50:
            cursor.execute(f"DELETE FROM messages WHERE chat_message_id = "
                           f"(SELECT chat_message_id from messages "
                           f"where chat_id = '{message.chat_id}' ORDER BY chat_message_id LIMIT 1)")
            conn.commit()

        if message.text is None:
            text = message.text

        cursor.execute(
            "INSERT INTO messages (chat_message_id, author_id, company_code, text, date, replied_message_id, chat_id) VALUES (%s, %s, %s, %s, %s, %s, %s);",
            (
                message.chat_message_id,
                message.author_id,
                message.company_code,
                message.text,
                message.date,
                message.replied_message_id,
                message.chat_id
            ),
        )
        conn.commit()

    @open_and_close_connection
    def get_count_messages_by_chat_id(self, chat_id, conn=None, cursor=None):
        cursor.execute(f"SELECT COUNT(*) FROM messages WHERE chat_id = {chat_id}")
        data = cursor.fetchone()[0]
        return data

    @open_and_close_connection
    def get_n_last_messages_by_chat_id(self, chat_id: int, bot_id: int, n: int, conn=None, cursor=None):
        cursor.execute(
            "SELECT * FROM messages "
            f"WHERE chat_id = {chat_id} "
            "ORDER BY message_id DESC "
            f"LIMIT {n};"
        )
        data = cursor.fetchall()
        users = {}
        result = []
        for row in data:
            msg = Message()
            msg.message_id = row[0]
            msg.chat_message_id = row[1]
            if row[2] == bot_id:
                msg.is_bot_message = True
            elif row[2] not in users:
                msg.is_bot_message = False
                users[row[2]] = self.users_repository.get_by_id(row[2])
            msg.author_id = row[2]
            if not msg.is_bot_message:
                msg.author_user = users[row[2]]
            msg.company_code = row[3]
            msg.text = row[4]
            msg.date = row[5].astimezone(pytz.timezone("Europe/Moscow"))
            msg.replied_message_id = row[6]
            result.append(msg)
        return result
