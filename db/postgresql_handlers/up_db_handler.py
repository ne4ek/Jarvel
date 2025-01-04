from infrastructure.repositories_impl.postgres.postgres_connection import open_and_close_connection

@open_and_close_connection
def user_is_uped_in_this_chat(username, chat_id, conn=None, cursor=None):
    query = "SELECT * from public.ups WHERE up_usernames = $1 AND chat_id = $2"
    cursor.execute(query, username, chat_id)
    data = cursor.fetchone()[0]
    return data