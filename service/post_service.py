import os
import json
import uuid
from pathlib import Path


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

        distancia_km = treino.distancia_metros / 1000

        prompt_base = f"""
        Gere 3 imagens verticais no formato 1080x1920 (TikTok/Reels).

        Use as imagens fornecidas como base visual.
        Integre todas as fotos de forma harmônica.

        Dados do treino:
        - Distância: {distancia_km:.2f} km
        - Tempo: {treino.tempo_formatado}
        - Pace: {treino.pace_formatado}
        - Calorias: {treino.calorias}

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