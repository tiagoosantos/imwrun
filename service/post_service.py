import os, time
import uuid
from pathlib import Path
from bot.utils.bot_utils import formatar_tempo, formatar_distancia


# ==========================
# PATHS BASE
# ==========================

BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp" / "posts"

TEMP_DIR.mkdir(parents=True, exist_ok=True)


# ==========================
# EXCEPTION CUSTOM
# ==========================

class LimiteDiarioExcedido(Exception):
    pass


# ==========================
# SERVICE
# ==========================

class PostService:

    LIMITE_DIARIO = 20

    def __init__(self, post_repository, corrida_service, post_generator, gemini_image_service):
        self.post_repository = post_repository
        self.corrida_service = corrida_service
        self.post_generator = post_generator
        self.gemini_image_service = gemini_image_service

    # ==========================
    # CONTROLE DE LIMITE
    # ==========================

    def pode_gerar_post(self, telegram_id):
        total = self.post_repository.contar_geracoes_hoje(telegram_id)
        return total < self.LIMITE_DIARIO

    # ==========================
    # FOTO TEMPORÁRIA
    # ==========================

    def salvar_foto_temporaria(self, image_bytes):

        filename = f"{uuid.uuid4()}.jpg"
        path = TEMP_DIR / filename

        with open(path, "wb") as f:
            f.write(image_bytes)

        return str(path)

    # ==========================
    # GERAR POST COMPLETO
    # ==========================

    def gerar_post(self, telegram_id, treino_id, fotos):

        if not self.pode_gerar_post(telegram_id):
            raise LimiteDiarioExcedido()

        # 🔹 Buscar treino
        treino = self.corrida_service.buscar_por_id(
            telegram_id=telegram_id,
            treino_id=treino_id
        )

        if not treino:
            raise ValueError("Treino não encontrado.")

        # treino = (id, distancia_metros, tempo_segundos, calorias, pace_segundos)
        distancia_metros = treino[1]
        tempo_segundos = treino[2]
        calorias = treino[3]
        pace_segundos = treino[4]

        # 🔹 Formatação usando suas utils
        distancia_km = formatar_distancia(distancia_metros)
        tempo_formatado = formatar_tempo(tempo_segundos)
        calorias_formatado = str(calorias) if calorias else "0"

        if pace_segundos:
            pace_formatado = formatar_tempo(pace_segundos) + "/km"
        else:
            pace_formatado = "N/A"

        # 🔹 Dados para o PostGenerator e Gemini
        dados = {
            "distancia": distancia_km,
            "tempo": tempo_formatado,
            "pace": pace_formatado,
            "calorias": calorias_formatado
        }

        imagens_geradas = []

        # =====================================
        # 1️⃣ GERAR 2 IMAGENS LOCAIS
        # =====================================
        imagens_locais = self.post_generator.gerar(
            fotos=fotos,
            dados=dados,
            quantidade=2   # <-- importante ajustar post_generator
        )

        imagens_geradas.extend(imagens_locais)

        # =====================================
        # 2️⃣ GERAR 1 IMAGEM VIA GEMINI
        # =====================================
        segundos = self.aguardar_limite_por_minuto()

        if segundos > 0:

            self.log.info(
                f"Limite por minuto atingido. Aguardando {segundos:.0f} segundos",
                extra={"telegram_id": telegram_id}
            )

            return {
                "aguardar" : True,
                "segundos": segundos
            }

        try:
            imagem_gemini = self.gemini_image_service.gerar_imagem_estilizada(
                telegram_id=telegram_id,
                image_path=fotos[0],  # usa primeira foto como base
                dados_treino=dados,
                prompt_usuario=None
            )

            imagens_geradas.append(imagem_gemini)

        except Exception:
            # fallback → gerar mais uma local
            fallback = self.post_generator.gerar(
                fotos=fotos,
                dados=dados,
                quantidade=1
            )

            imagens_geradas.extend(fallback)

        # =====================================
        # 3️⃣ REGISTRAR NO BANCO
        # =====================================
        self.post_repository.registrar_geracao(telegram_id)

        return imagens_geradas

    # ==========================
    # LIMPAR ARQUIVOS TEMPORÁRIOS
    # ==========================

    def limpar_arquivos(self, arquivos):

        for path in arquivos:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception:
                pass

    def aguardar_limite_por_minuto(self):

        LIMITE_POR_MINUTO = 15

        while True:

            ultimos_60s = self.post_repository.contar_geracoes_ultimos_60s()
            minuto_atual = self.post_repository.contar_geracoes_minuto_atual()

            if ultimos_60s < LIMITE_POR_MINUTO and minuto_atual < LIMITE_POR_MINUTO:
                return 0
            
            segundos_restantes = 60 - (time.time() % 60)
            return segundos_restantes
