from psycopg2 import pool
import os
from typing import Any
from dotenv import load_dotenv



load_dotenv()
conn: Any = None
cur: Any = None


connection_pool = pool.ThreadedConnectionPool(
    1,
    20,
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    database=os.getenv("DB_NAME"),
    keepalives=1,
    keepalives_idle=60,
    keepalives_interval=15,
    keepalives_count=10
)