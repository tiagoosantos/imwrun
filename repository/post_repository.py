from database.connection import get_connection


class PostRepository:
    """
    Responsável apenas por persistência das gerações de posts.
    Nenhuma regra de negócio deve ficar aqui.
    """

    # ======================================================
    # CONTAR GERAÇÕES DO DIA
    # ======================================================

    def contar_geracoes_hoje(self, telegram_id: int) -> int:

        conn = get_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*)
                    FROM public.post_geracoes
                    WHERE telegram_id = %s
                      AND data_geracao = CURRENT_DATE
                    """,
                    (telegram_id,)
                )

                result = cur.fetchone()
                return result[0] if result else 0

        finally:
            conn.close()

    # ======================================================
    # REGISTRAR GERAÇÃO
    # ======================================================

    def registrar_geracao(self, telegram_id: int) -> None:

        conn = get_connection()

        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO public.post_geracoes (telegram_id)
                    VALUES (%s)
                    """,
                    (telegram_id,)
                )

            conn.commit()

        finally:
            conn.close()