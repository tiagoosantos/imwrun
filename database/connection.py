import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from config.settings import (IMW_HOST, IMW_USER, IMW_PASS, IMW_PORT, IMW_DB)

_pool = None


def init_pool(minconn=1, maxconn=10):
    global _pool

    if _pool is None:
        _pool = ThreadedConnectionPool(
            minconn,
            maxconn,
            host=IMW_HOST,
            port=int(IMW_PORT),
            database=IMW_DB,
            user=IMW_USER,
            password=IMW_PASS,
            options="-c client_encoding=UTF8"
        )


def get_connection():
    if _pool is None:
        raise RuntimeError("Pool não inicializado.")
    return _pool.getconn()


def release_connection(conn):
    if _pool:
        _pool.putconn(conn)
