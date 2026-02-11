from repository.corrida_repository import CorridaRepository


class CorridaService:
    def __init__(self):
        self.repo = CorridaRepository()

    # =========================
    # REGRA DE NEGÓCIO
    # =========================

    def calcular_pace(self, tempo_segundos: int, distancia_km: float) -> int:
        if distancia_km <= 0:
            raise ValueError("Distância deve ser maior que zero")

        return int(tempo_segundos / distancia_km)

    # =========================
    # REGISTRO
    # =========================

    def registrar_corrida(
        self,
        telegram_id: int,
        tempo_segundos: int,
        distancia_km: float,
        passos: int | None,
        calorias: int | None,
        pace_segundos: int | None = None,  # 👈 opcional
    ) -> None:
        """
        Regra:
        - Se pace for informado manualmente → usar ele
        - Senão → calcular automaticamente
        """

        if pace_segundos is None:
            pace_segundos = self.calcular_pace(
                tempo_segundos,
                distancia_km,
            )

        self.repo.inserir_corrida(
            telegram_id=telegram_id,
            tempo_segundos=tempo_segundos,
            distancia_km=distancia_km,
            passos=passos,
            calorias=calorias,
            pace_segundos=pace_segundos,
        )
