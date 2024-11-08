from application.repositories.ctrls_repository import CtrlsRepository
from domain.entities.ctrl_message import CtrlMessage
from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection
from psycopg2.pool import ThreadedConnectionPool


class PostgresCtrlsRepository(CtrlsRepository):
    def __init__(self, db_connection_pool: ThreadedConnectionPool):
        self.db_connection_pool = db_connection_pool
    
    @open_and_close_connection
    def save(self, ctrl_message: CtrlMessage, conn=None, cursor=None):
        query = "INSERT INTO ctrls (run_date, chat_id, ctrl_usernames, reply_message_id, fyi_usernames) VALUES (%s, %s, %s, %s, %s)"
        values = (ctrl_message.run_date, ctrl_message.chat_id, ctrl_message.ctrl_usernames, ctrl_message.reply_message_id, ctrl_message.fyi_usernames)
        cursor.execute(query, values)
        conn.commit()
    
    @open_and_close_connection
    def get_all(self, conn=None, cursor=None):
        query = "SELECT * FROM ctrls"
        cursor.execute(query)
        ctrls = cursor.fetchall()
        result = []
        for row in ctrls:
            result.append(CtrlMessage(*row))
        print(result)
        return result
        