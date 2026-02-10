# %%
import psycopg2
from config.settings import (IMW_HOST, IMW_USER, IMW_PASS, IMW_PORT, IMW_DB)


def get_connection():
    if not all([IMW_HOST, IMW_DB, IMW_USER, IMW_PASS, IMW_PORT]):
        raise RuntimeError("Credenciais do banco não configuradas corretamente.")

    return psycopg2.connect(
        host=IMW_HOST,
        port=int(IMW_PORT),
        database=IMW_DB,
        user=IMW_USER,
        password=IMW_PASS,
        options="-c client_encoding=UTF8"
    )
