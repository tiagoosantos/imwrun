from database.connection import get_connection


class CorridaRepository:
    """
    Responsável apenas por persistência e leitura de dados de corridas.
    Nenhuma regra de negócio deve ficar aqui.
    """

    def inserir_corrida(
        self,
        telegram_id: int,
        tempo_minutos: int,
        distancia_km: float,
        passos: int | None,
        calorias: int | None,
        pace: float,
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
                    tempo_minutos,
                    distancia_km,
                    passos,
                    calorias,
                    pace
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    telegram_id,
                    tempo_minutos,
                    distancia_km,
                    passos,
                    calorias,
                    pace,
                ),
            )
            conn.commit()

        finally:
            cur.close()
            conn.close()

    # --------------------------------------------------

    def listar_corridas_usuario(self, telegram_id: int):
        """
        Retorna todas as corridas de um usuário.
        """

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT
                    id,
                    tempo_minutos,
                    distancia_km,
                    passos,
                    calorias,
                    pace,
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

    def ranking_km(self, limit: int = 10):
        """
        Ranking por quilometragem total.
        """

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT
                    u.telegram_id,
                    u.nome,
                    ROUND(SUM(c.distancia_km), 2) AS total_km
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

    def ranking_tempo(self, limit: int = 10):
        """
        Ranking por tempo total de exercício.
        """

        conn = get_connection()
        cur = conn.cursor()

        try:
            cur.execute(
                """
                SELECT
                    u.telegram_id,
                    u.nome,
                    SUM(c.tempo_minutos) AS tempo_total
                FROM usuarios u
                JOIN corridas c ON c.telegram_id = u.telegram_id
                GROUP BY u.telegram_id, u.nome
                ORDER BY tempo_total DESC
                LIMIT %s
                """,
                (limit,),
            )

            return cur.fetchall()

        finally:
            cur.close()
            conn.close()
