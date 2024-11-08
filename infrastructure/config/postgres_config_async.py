
import asyncpg
import os
from dotenv import load_dotenv
from icecream import ic

load_dotenv()

connection_pool = None

async def create_pool():
    global connection_pool
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    host = os.getenv("POSTGRES_HOST")
    port = os.getenv("POSTGRES_PORT")
    database = os.getenv("POSTGRES_DB")
    ic(user, password, host, port, database)
    connection_pool = await asyncpg.create_pool(user=user,
    password=password,
    host=host,
    port=port,
    database=database)

def get_connection_pool():
    global connection_pool
    # ic(connection_pool)
    return connection_pool    
