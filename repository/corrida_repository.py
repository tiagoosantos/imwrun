from database.connection import get_connection


class CorridaRepository:
    """
    Responsável apenas por persistência e leitura de dados de corridas.
    Nenhuma regra de negócio deve ficar aqui.
    """

    # --------------------------------------------------
    # INSERT
    # --------------------------------------------------

    def inserir_corrida(
        self,
        telegram_id: int,
        tempo_segundos: int,
        distancia_metros: int,
        passos: int | None,
        calorias: int | None,
        pace_segundos: int,
        pace_origem: str,
    ) -> None:
        """
        Insere uma nova corrida para um usuário já existente.
        """

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                INSERT INTO corridas (
                    telegram_id,
                    tempo_segundos,
                    distancia_metros,
                    passos,
                    calorias,
                    pace_segundos,
                    pace_origem
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    telegram_id,
                    tempo_segundos,
                    distancia_metros,
                    passos,
                    calorias,
                    pace_segundos,
                    pace_origem,
                ),
            )

            conn.commit()

        finally:
            cur.close()
            conn.close()

    # --------------------------------------------------
    # LISTAR CORRIDAS DO USUÁRIO
    # --------------------------------------------------

    def listar_corridas_usuario(self, telegram_id: int):

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT
                    id,
                    tempo_segundos,
                    distancia_metros,
                    passos,
                    calorias,
                    pace_segundos,
                    pace_origem,
                    data_corrida
                FROM corridas
                WHERE telegram_id = %s
                ORDER BY data_corrida DESC
                """,
                (telegram_id,),
            )

            return cur.fetchall()

        finally:
            cur.close()
            conn.close()

    # --------------------------------------------------
    # RANKING KM
    # --------------------------------------------------

    def ranking_km(self, limit: int = 10):

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT
                    u.telegram_id,
                    u.nome,
                    ROUND(SUM(c.distancia_metros) / 1000.0, 2) AS total_km
                FROM usuarios u
                JOIN corridas c ON c.telegram_id = u.telegram_id
                GROUP BY u.telegram_id, u.nome
                ORDER BY total_km DESC
                LIMIT %s
                """,
                (limit,),
            )

            return cur.fetchall()

        finally:
            cur.close()
            conn.close()

    # --------------------------------------------------
    # RANKING TEMPO
    # --------------------------------------------------

    def ranking_tempo(self, limit: int = 10):

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT
                    u.telegram_id,
                    u.nome,
                    SUM(c.tempo_segundos) AS tempo_total_segundos
                FROM usuarios u
                JOIN corridas c ON c.telegram_id = u.telegram_id
                GROUP BY u.telegram_id, u.nome
                ORDER BY tempo_total_segundos DESC
                LIMIT %s
                """,
                (limit,),
            )

            return cur.fetchall()

        finally:
            cur.close()
            conn.close()
