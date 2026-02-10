from repository.corrida_repository import CorridaRepository


class CorridaService:
    def __init__(self):
        self.repo = CorridaRepository()

    def calcular_pace(self, tempo_minutos: int, distancia_km: float) -> float:
        return round(tempo_minutos / distancia_km, 2)

    def registrar_corrida(
        self,
        telegram_id: int,
        tempo_minutos: int,
        distancia_km: float,
        passos: int | None,
        calorias: int | None,
    ) -> None:
        """
        Regra de negócio:
        - calcula pace
        - delega persistência ao repository
        """

        pace = self.calcular_pace(tempo_minutos, distancia_km)

        self.repo.inserir_corrida(
            telegram_id=telegram_id,
            tempo_minutos=tempo_minutos,
            distancia_km=distancia_km,
            passos=passos,
            calorias=calorias,
            pace=pace,
        )
