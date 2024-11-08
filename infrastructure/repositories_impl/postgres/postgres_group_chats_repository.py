from domain.entities.group_chat import GroupChat
from application.repositories.group_chats_repository import GroupChatsRepository
from psycopg2.pool import ThreadedConnectionPool
from domain.entities.group_chat import GroupChat

from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection


class PostgresGroupChatsRepository(GroupChatsRepository):
    def __init__(self, db_connection_pool: ThreadedConnectionPool):
        self.db_connection_pool = db_connection_pool

    @open_and_close_connection
    def get_company_code(self, chat_id: int, conn=None, cursor=None):
        cursor.execute(f"SELECT company_code FROM group_chats WHERE chat_id = '{chat_id}'")
        data = cursor.fetchone()[0]
        return data

    @open_and_close_connection
    def get_all_chat_ids(self, conn=None, cursor=None):
        cursor.execute(f"SELECT chat_id FROM group_chats")
        data = cursor.fetchone()
        return data
    
    @open_and_close_connection
    def get_by_chat_id(self, chat_id: int, conn=None, cursor=None):
        cursor.execute(f"SELECT * FROM group_chats WHERE chat_id = {chat_id}")
        gc = cursor.fetchone()
        
        return GroupChat(*gc)
    
    

    @open_and_close_connection
    def save_group_chat(self, group_chat: GroupChat, conn=None, cursor=None):
        cursor.execute(
            "INSERT INTO group_chats (chat_id, name, company_code, owner_id) "
            "VALUES (%s, %s, %s, %s);",
            (group_chat.chat_id, group_chat.name,
             group_chat.company_code, group_chat.owner_id),
        )
        conn.commit()

    @open_and_close_connection
    def is_group_chat_exists(self, group_chat: GroupChat, conn=None, cursor=None):
        cursor.execute(
            f"SELECT EXISTS(SELECT 1 FROM group_chats WHERE chat_id = '{group_chat.chat_id}' AND company_code = '{group_chat.company_code}')"
        )

        data = cursor.fetchone()[0]
        return data

    @open_and_close_connection
    def get_name_by_chat_id(self, chat_id: int, conn=None, cursor=None):
        cursor.execute(f"SELECT name FROM group_chats WHERE chat_id = '{chat_id}'")
        data = cursor.fetchone()[0]
        return data

    @open_and_close_connection
    def delete(self, chat_id: int, conn=None, cursor=None):
        cursor.execute(f"DELETE FROM group_chats WHERE chat_id = '{chat_id}'")
        conn.commit()

    @open_and_close_connection
    def is_chat_id_exists(self, chat_id: int, conn=None, cursor=None):
        cursor.execute(f"SELECT EXISTS(SELECT 1 FROM group_chats WHERE chat_id = '{chat_id}')")
        data = cursor.fetchone()[0]
        return data

    @open_and_close_connection
    def is_group_chat_assigned_to_company(self, chat_id: int, conn=None, cursor=None) -> bool:
        cursor.execute(f"SELECT company_code FROM group_chats WHERE chat_id = %s", (chat_id,))
        company_code = cursor.fetchone()
        if company_code:
            return True
        else:
            return False