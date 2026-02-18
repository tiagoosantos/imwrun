from typing import Optional, Callable, Any
from functools import wraps

from repository.corrida_repository import CorridaRepository
from database.transaction import transactional, readonly


class CorridaService:

    # ------------------------------------------------------
    # REGRA DE NEGÓCIO
    # ------------------------------------------------------

    def calcular_pace(
        self,
        tempo_segundos: int,
        distancia_metros: int
    ) -> int:
        """
        Calcula pace em segundos por km.
        """

        if distancia_metros <= 0:
            raise ValueError("Distância deve ser maior que zero")

        if tempo_segundos <= 0:
            raise ValueError("Tempo deve ser maior que zero")

        return int((tempo_segundos * 1000) / distancia_metros)

    # ------------------------------------------------------
    # REGISTRO DE CORRIDA
    # ------------------------------------------------------

    @transactional
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
        *,
        conn=None
    ) -> None:
        """
        Registra uma nova corrida.
        """

        if tempo_segundos <= 0:
            raise ValueError("Tempo inválido")

        if distancia_metros <= 0:
            raise ValueError("Distância inválida")

        if pace_segundos is not None and pace_segundos <= 0:
            raise ValueError("Pace inválido")

        # Se não foi informado manualmente, calcula
        if pace_segundos is None:
            pace_segundos = self.calcular_pace(
                tempo_segundos,
                distancia_metros
            )
            pace_origem = "calculado"
        else:
            pace_origem = "manual"

        tipo_treino = tipo_treino.lower().strip()
        local_treino = local_treino.lower().strip()

        repo = CorridaRepository(conn)

        repo.inserir_corrida(
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

    # ------------------------------------------------------
    # RANKINGS
    # ------------------------------------------------------

    @readonly
    def obter_ranking_km(
        self,
        limit: int,
        offset: int = 0,
        *,
        conn=None
    ):
        repo = CorridaRepository(conn)
        return repo.ranking_km(limit, offset)

    @readonly
    def obter_ranking_tempo(
        self,
        limit: int,
        *,
        conn=None
    ):
        repo = CorridaRepository(conn)
        return repo.ranking_tempo(limit)

    # ------------------------------------------------------
    # RELATÓRIO INDIVIDUAL
    # ------------------------------------------------------

    @readonly
    def obter_estatisticas_usuario(
        self,
        telegram_id: int,
        *,
        conn=None
    ):
        repo = CorridaRepository(conn)
        return repo.estatisticas_usuario(telegram_id)
