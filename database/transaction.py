import time
from functools import wraps
from typing import Callable, Any

import psycopg2
from database.connection import get_connection, release_connection


# ==========================================================
# CONFIGURAÇÕES
# ==========================================================

MAX_RETRIES = 3
RETRY_DELAY = 0.2  # segundos


# ==========================================================
# DECORATOR TRANSACIONAL COM RETRY
# ==========================================================

def transactional(func: Callable) -> Callable:
    """
    - Controla transação
    - Commit automático
    - Rollback automático
    - Retry automático em deadlock
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:

        attempt = 0

        while attempt < MAX_RETRIES:
            conn = get_connection()

            try:
                result = func(*args, conn=conn, **kwargs)
                conn.commit()
                return result

            except psycopg2.errors.DeadlockDetected:
                conn.rollback()
                attempt += 1

                if attempt >= MAX_RETRIES:
                    raise

                time.sleep(RETRY_DELAY)

            except Exception:
                conn.rollback()
                raise

            finally:
                release_connection(conn)

    return wrapper


# ==========================================================
# DECORATOR SOMENTE LEITURA
# ==========================================================

def readonly(func: Callable) -> Callable:
    """
    Para consultas.
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        conn = get_connection()

        try:
            return func(*args, conn=conn, **kwargs)

        finally:
            release_connection(conn)

    return wrapper
