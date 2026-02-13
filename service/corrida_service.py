from repository.corrida_repository import CorridaRepository


class CorridaService:

    def __init__(self):
        self.repo = CorridaRepository()

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
        passos: int | None,
        calorias: int | None,
        tipo_treino: str,
        local_treino: str,
        pace_segundos: int | None = None,
    ) -> None:
        """
        Regra:
        - Se pace for informado manualmente → usar ele
        - Senão → calcular automaticamente
        """

        if tempo_segundos <= 0:
            raise ValueError("Tempo inválido")

        if distancia_metros <= 0:
            raise ValueError("Distância inválida")

        # -------------------------
        # PACE
        # -------------------------

        if pace_segundos is None:
            pace_segundos = self.calcular_pace(
                tempo_segundos,
                distancia_metros,
            )
            pace_origem = "calculado"
        else:
            pace_origem = "manual"

        # -------------------------
        # NORMALIZAÇÃO NOVA
        # -------------------------

        tipo_treino = tipo_treino.lower().strip()
        local_treino = local_treino.lower().strip()

        # -------------------------
        # PERSISTÊNCIA
        # -------------------------

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
