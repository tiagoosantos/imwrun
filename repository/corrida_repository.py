class CorridaRepository:
    """
    Responsável apenas por persistência e leitura de dados de corridas.
    Nenhuma regra de negócio deve ficar aqui.
    """

    def __init__(self, connection):
        self.conn = connection

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
        tipo_treino: str,
        local_treino: str,
        data_corrida=None,  # ✅ NOVO
    ) -> None:
        """
        Insere uma nova corrida para um usuário já existente.
        """

        with self.conn.cursor() as cur:

            # --------------------------------------------------
            # Se data_corrida for informada → inclui no INSERT
            # Senão → usa default do banco (CURRENT_TIMESTAMP)
            # --------------------------------------------------

            if data_corrida is not None:
                cur.execute(
                    """
                    INSERT INTO corridas (
                        telegram_id,
                        tempo_segundos,
                        distancia_metros,
                        passos,
                        calorias,
                        pace_segundos,
                        pace_origem,
                        tipo_treino,
                        local_treino,
                        data_corrida
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        telegram_id,
                        tempo_segundos,
                        distancia_metros,
                        passos,
                        calorias,
                        pace_segundos,
                        pace_origem,
                        tipo_treino,
                        local_treino,
                        data_corrida,
                    ),
                )
            else:
                cur.execute(
                    """
                    INSERT INTO corridas (
                        telegram_id,
                        tempo_segundos,
                        distancia_metros,
                        passos,
                        calorias,
                        pace_segundos,
                        pace_origem,
                        tipo_treino,
                        local_treino
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        telegram_id,
                        tempo_segundos,
                        distancia_metros,
                        passos,
                        calorias,
                        pace_segundos,
                        pace_origem,
                        tipo_treino,
                        local_treino,
                    ),
                )

    # --------------------------------------------------
    # LISTAR CORRIDAS DO USUÁRIO
    # --------------------------------------------------

    def listar_corridas_usuario(self, telegram_id: int, limite: int) -> list[tuple]:

        with self.conn.cursor() as cur:
            # cur.execute(
            #     """
            #     SELECT
            #         id,
            #         tempo_segundos,
            #         distancia_metros,
            #         passos,
            #         calorias,
            #         pace_segundos,
            #         pace_origem,
            #         data_corrida,
            #         tipo_treino,
            #         local_treino
            #     FROM corridas
            #     WHERE telegram_id = %s
            #     ORDER BY data_corrida DESC
            #     """,
            #     (telegram_id,),
            # )
            cur.execute(
                            """
                            SELECT
                                id,
                                tempo_segundos,
                                distancia_metros
                            FROM corridas
                            WHERE telegram_id = %s
                            ORDER BY data_corrida DESC
                            LIMIT %s
                            """,
                            (telegram_id, limite),
                        )

            return cur.fetchall()
        
    # --------------------------------------------------
    # LISTAR CORRIDAS DE USUÁRIO POR ID (para gerar post)
    # --------------------------------------------------

    def buscar_por_id(self, telegram_id: int, treino_id: int):

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id,
                    distancia_metros,
                    tempo_segundos,
                    calorias,
                    pace_segundos
                FROM public.corridas
                WHERE telegram_id = %s
                AND id = %s
                """,
                (telegram_id, treino_id)
            )

            return cur.fetchone()
        
    # --------------------------------------------------
    # RANKING KM
    # --------------------------------------------------

    def ranking_km(self, limit: int = 10, offset: int = 0):

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    u.telegram_id,
                    u.nome,
                    ROUND(COALESCE(SUM(c.distancia_metros), 0) / 1000.0, 2) AS total_km
                FROM usuarios u
                LEFT JOIN corridas c ON c.telegram_id = u.telegram_id
                WHERE u.nome_confirmado = TRUE
                GROUP BY u.telegram_id, u.nome
                ORDER BY total_km DESC
                LIMIT %s OFFSET %s
                """,
                (limit, offset),
            )

            return cur.fetchall()

    # --------------------------------------------------
    # RANKING TEMPO
    # --------------------------------------------------

    def ranking_tempo(self, limit: int = 10):

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    u.telegram_id,
                    u.nome,
                    COALESCE(SUM(c.tempo_segundos), 0) AS tempo_total_segundos
                FROM usuarios u
                LEFT JOIN corridas c ON c.telegram_id = u.telegram_id
                WHERE u.nome_confirmado = TRUE
                GROUP BY u.telegram_id, u.nome
                ORDER BY tempo_total_segundos DESC
                LIMIT %s
                """,
                (limit,),
            )

            return cur.fetchall()