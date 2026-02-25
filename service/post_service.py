import os
import json
import uuid
from pathlib import Path
from bot.utils.bot_utils import formatar_tempo, formatar_distancia


# ==========================
# PATHS BASE
# ==========================

BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp" / "posts"
PROMPTS_PATH = BASE_DIR / "assets" / "templates" / "prompts.json"

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

    LIMITE_DIARIO = 2

    def __init__(self, post_repository, corrida_service, post_generator):
        self.post_repository = post_repository
        self.corrida_service = corrida_service
        self.post_generator = post_generator
        self.prompts = self._carregar_prompts()

    # ==========================
    # CONTROLE DE LIMITE
    # ==========================

    def pode_gerar_post(self, telegram_id):

        total = self.post_repository.contar_geracoes_hoje(telegram_id)
        return total < self.LIMITE_DIARIO

    # ==========================
    # PROMPTS
    # ==========================

    def _carregar_prompts(self):
        if not PROMPTS_PATH.exists():
            return {}

        with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    def listar_prompts_modelo(self):
        return {
            key: value["titulo"]
            for key, value in self.prompts.items()
        }

    def obter_prompt_modelo(self, key):
        return self.prompts[key]["texto"]

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

    def gerar_post(self, telegram_id, treino_id, fotos, prompt_usuario):

        if not self.pode_gerar_post(telegram_id):
            raise LimiteDiarioExcedido()

        # Buscar dados do treino
        treino = self.corrida_service.buscar_por_id(
            telegram_id=telegram_id,
            treino_id=treino_id
        )

        # Montar prompt final estruturado
        prompt_final = self._montar_prompt(treino, prompt_usuario)

        # Gerar imagens via Gemini
        imagens_geradas = self.post_generator.gerar(
            fotos=fotos,
            prompt=prompt_final
        )

        # Registrar no banco
        self.post_repository.registrar_geracao(telegram_id)

        return imagens_geradas

    # ==========================
    # MONTAR PROMPT FINAL
    # ==========================

    def _montar_prompt(self, treino, prompt_usuario):

        if not treino:
            raise ValueError("Treino não encontrado.")

        # treino = (id, distancia_metros, tempo_segundos, calorias, pace_segundos)
        distancia_metros = treino[1]
        tempo_segundos = treino[2]
        calorias = treino[3]
        pace_segundos = treino[4]

        distancia_km = formatar_distancia(distancia_metros)
        tempo_formatado = formatar_tempo(tempo_segundos)
        calorias_formatado = f"{calorias} kcal" if calorias else "N/A"
        pace_formatado = formatar_tempo(pace_segundos) + " /km" if pace_segundos else "N/A"

        prompt_base = f"""
        Gere 3 imagens verticais no formato 1080x1920 (TikTok/Reels).

        Use as imagens fornecidas como base visual.
        Integre todas as fotos de forma harmônica.

        Dados do treino:
        - Distância: {distancia_km} km
        - Tempo: {tempo_formatado}
        - Pace: {pace_formatado}
        - Calorias: {calorias_formatado}

        Requisitos obrigatórios:
        - Estilo esportivo moderno
        - Contraste alto
        - Tipografia forte e legível
        - Layout impactante
        - Cada imagem deve ter composição diferente
        - Cada imagem deve ter frase motivacional diferente
        - Manter identidade visual consistente
        """

        return prompt_base + "\n\nEstilo adicional solicitado:\n" + prompt_usuario

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