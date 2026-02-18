from repository.corrida_repository import CorridaRepository
from typing import Optional


class CorridaService:

    def __init__(self, connection):
        self.repo = CorridaRepository(connection)

    # =========================
    # REGRA DE NEGÓCIO
    # =========================

    def calcular_pace(
        self,
        tempo_segundos: int,
        distancia_metros: int
    ) -> int:

        if distancia_metros <= 0:
            raise ValueError("Distância deve ser maior que zero")

        return int((tempo_segundos * 1000) / distancia_metros)

    # =========================
    # REGISTRO
    # =========================

    def registrar_corrida(
        self,
        telegram_id: int,
        tempo_segundos: int,
        distancia_metros: int,
        passos: Optional[int],
        calorias: Optional[int],
        tipo_treino: str,
        local_treino: str,
        pace_segundos: Optional[int] = None,
    ) -> None:

        if tempo_segundos <= 0:
            raise ValueError("Tempo inválido")

        if distancia_metros <= 0:
            raise ValueError("Distância inválida")

        if pace_segundos is not None and pace_segundos <= 0:
            raise ValueError("Pace inválido")

        if pace_segundos is None:
            pace_segundos = self.calcular_pace(
                tempo_segundos,
                distancia_metros,
            )
            pace_origem = "calculado"
        else:
            pace_origem = "manual"

        tipo_treino = tipo_treino.lower().strip()
        local_treino = local_treino.lower().strip()

        self.repo.inserir_corrida(
            telegram_id=telegram_id,
            tempo_segundos=tempo_segundos,
            distancia_metros=distancia_metros,
            passos=passos,
            calorias=calorias,
            pace_segundos=pace_segundos,
            pace_origem=pace_origem,
            tipo_treino=tipo_treino,
            local_treino=local_treino,
        )

    # =========================
    # RANKING
    # =========================

    def obter_ranking_km(self, limit: int, offset: int = 0):
        return self.repo.ranking_km(limit, offset)

    def obter_ranking_tempo(self, limit: int):
        return self.repo.ranking_tempo(limit)
