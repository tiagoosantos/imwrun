from repository.corrida_repository import CorridaRepository


class CorridaService:
    def __init__(self):
        self.repo = CorridaRepository()

    def calcular_pace(self, tempo, distancia):
        return round(tempo / distancia, 2)

    def registrar_corrida(self, telegram_id, nome, tempo, distancia, passos, calorias):
        pace = self.calcular_pace(tempo, distancia)
        self.repo.inserir_corrida(
            telegram_id, nome, tempo, distancia, passos, calorias, pace
        )
