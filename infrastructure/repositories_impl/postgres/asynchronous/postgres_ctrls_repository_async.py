from application.repositories.ctrls_repository import CtrlsRepository
from domain.entities.ctrl_message import CtrlMessage
from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection


class PostgresCtrlsRepositoryAsync(CtrlsRepository):
    def __init__(self, db_connection_pool):
        self.db_connection_pool = db_connection_pool
    
    @open_and_close_connection
    async def save(self, ctrl_message: CtrlMessage, connection=None):
        query = """
            INSERT INTO ctrls (run_date, chat_id, ctrl_usernames, reply_message_id, fyi_usernames)
            VALUES ($1, $2, $3, $4, $5)
        """
        await connection.execute(query,
                                ctrl_message.run_date,
                                ctrl_message.chat_id,
                                ctrl_message.ctrl_usernames,
                                ctrl_message.reply_message_id,
                                ctrl_message.fyi_usernames)

       
    
    @open_and_close_connection
    async def get_all(self, connection=None):
        query = "SELECT * FROM ctrls"
        result = await connection.fetch(query)
        rows = []
        for row in result:
            row_list = [row.get("chat_id"), row.get("run_date"), row.get("ctrl_usernames"), row.get("reply_message_id"), row.get("fyi_usernames")]
            rows.append(CtrlMessage(*row_list))
        print(rows)
        return rows

            