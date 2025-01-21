from infrastructure.repositories_impl.postgres.asynchronous.postgres_connection_async import open_and_close_connection



class PostgresTranscribedVoiceMessageTextAsync:
    def __init__(self, db_connection_pool):
        self._connection_pool = db_connection_pool
        
        
    @open_and_close_connection
    async def save(self, transcribed_voice_message_text: str, connection=None):
        query = "INSERT INTO public.transcribed_voice_message_text(text) VALUES ($1) RETURNING transcribed_voice_message_text_id"
        transcribed_voice_message_text_id = await connection.fetchval(query, transcribed_voice_message_text)
        return transcribed_voice_message_text_id
        
        
    @open_and_close_connection
    async def get_text_by_id(self, id: int, connection=None):
        query = "SELECT text FROM public.transcribed_voice_message_text WHERE transcribed_voice_message_text_id = $1"
        result = await connection.fetch(query, id)
        return result[0].get("text")