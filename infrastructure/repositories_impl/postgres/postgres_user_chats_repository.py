from domain.entities.user_chat import UserChat
from application.repositories.user_chats_repository import UserChatsRepository
from psycopg2.pool import ThreadedConnectionPool

from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection



class PostgresUserChatsRepository(UserChatsRepository):
    def __init__(self, db_connection_pool: ThreadedConnectionPool):
        self.db_connection_pool = db_connection_pool

    @open_and_close_connection
    def get_by_id(self, user_id: int, conn=None, cursor=None) -> UserChat:
        cursor.execute("SELECT * FROM user_chats")
        data = cursor.fetchall()
        return data

    @open_and_close_connection
    def get_user_id_by_company_code(self, company_code: str, conn=None, cursor=None):
        cursor.execute(f"SELECT chat_id FROM user_chats WHERE company_code = '{company_code}'")
        data = cursor.fetchone()[0]
        return data

    @open_and_close_connection
    def get_companies_codes_by_user_id(self, chat_id: int, conn=None, cursor=None):
        cursor.execute(f"SELECT company_code FROM user_chats WHERE chat_id = '{chat_id}'")
        data = cursor.fetchall()
        return data

    @open_and_close_connection
    def save_user_chat(self, user_chat: UserChat, conn=None, cursor=None):
        cursor.execute("INSERT INTO user_chats (chat_id, role, company_code) "
                       "VALUES (%s, %s, %s)",
                       (user_chat.user_id, user_chat.role, user_chat.company_code))
        conn.commit()

    @open_and_close_connection
    def is_user_chat_exists(self, user_chat: UserChat, conn=None, cursor=None):
        
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM user_chats WHERE chat_id = '{user_chat.user_id}' "
                       f"AND role = '{user_chat.role}' "
                       f"AND company_code = '{user_chat.company_code}')")
        data = cursor.fetchone()[0]
        return data
