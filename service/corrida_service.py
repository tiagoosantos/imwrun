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

        # pace = tempo por km
        # km = metros / 1000
        # pace = tempo / (metros/1000)
        # pace = tempo * 1000 / metros
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

        if pace_segundos is None:
            pace_segundos = self.calcular_pace(
                tempo_segundos,
                distancia_metros,
            )
            pace_origem = "calculado"
        else:
            pace_origem = "manual"

        self.repo.inserir_corrida(
            telegram_id=telegram_id,
            tempo_segundos=tempo_segundos,
            distancia_metros=distancia_metros,
            passos=passos,
            calorias=calorias,
            pace_segundos=pace_segundos,
            pace_origem=pace_origem,
        )
