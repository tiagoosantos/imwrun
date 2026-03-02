import os
import time
import logging
import base64
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError
import telegramify_markdown
from config.settings import GEMINI
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

log = logging.getLogger(__name__)

# =========================
# Configurações gerais
# =========================

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTRUCOES_FILE = os.path.join(BASE_PATH, "ia", "instrucoes_gemini.txt")

# modelos em ordem de prioridade
MODELOS = [
    "gemini-3-flash-preview",  # rápido (preview, pode falhar)
    "gemini-2.5-pro",          # estável
    "gemini-2.0-pro",          # fallback final
]

# histórico curto por usuário
chat_sessions = {}

# cache simples para perguntas repetidas
cache_respostas = {}

# client Gemini (API nova)
client = genai.Client(api_key=GEMINI)


# =========================
# Utilitários
# =========================

def carregar_instrucoes():
    try:
        with open(INSTRUCOES_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        log.warning("instrucoes_gemini.txt não encontrado")
        return ""


def gerar_resposta(prompt: str) -> str:
    """
    Tenta gerar resposta usando modelos em fallback.
    """
    ultimo_erro = None

    for modelo in MODELOS:
        try:
            inicio = time.perf_counter()

            response = client.models.generate_content(
                model=modelo,
                contents=prompt,
            )

            duracao = time.perf_counter() - inicio
            log.info(f"Gemini respondeu com {modelo} em {duracao:.2f}s")

            return response.text.strip()

        except ServerError as e:
            # 503 / indisponibilidade temporária
            log.warning(f"Modelo {modelo} indisponível, tentando fallback")
            ultimo_erro = e
            continue

        except ClientError as e:
            # erro de configuração (key, projeto, etc.)
            log.error("Erro de configuração Gemini", exc_info=e)
            break

    raise RuntimeError("Nenhum modelo Gemini disponível") from ultimo_erro


# =========================
# Handler principal
# =========================

def responder_com_ia(bot, message):
    texto_usuario = message.text.strip()
    user_id = message.from_user.id

    # filtros básicos (reduz custo e latência)
    # if not texto_usuario or len(texto_usuario) < 6:
    if not texto_usuario:
        return
    
    cumprimentos = {
        "oi": "👋 Olá! Posso te ajudar com treinos, ranking ou pace.",
        "olá": "👋 Olá! Quer registrar um treino ou ver o ranking?",
        "ola": "👋 Olá! Quer registrar um treino ou ver o ranking?",
        "bom dia": "🌅 Bom dia! Bora correr hoje?",
        "boa tarde": "☀️ Boa tarde! Como posso ajudar?",
        "boa noite": "🌙 Boa noite! Quer ver seu desempenho?",
        "b dia": "🌅 Bom dia! Bora correr hoje?",
    }

    chama_funcao = ("\n\n Se preferir temos uma lista de comandos disponíveis\n Para acessar basta clicar no botão abaixo 👇")

    if texto_usuario in cumprimentos:
        # bot.send_message(message.chat.id, cumprimentos[texto_usuario] + chama_funcao)
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                "📋 Ver comandos",
                url="https://t.me/IMW_Runners_bot?start=menu"
            )
        )

        bot.send_message(
            message.chat.id,
            cumprimentos[texto_usuario] + chama_funcao,
            reply_markup=markup
        )
        return

    if len(texto_usuario) < 4:
        fake_message = message
        fake_message.text = "/start"
        bot.process_new_messages([fake_message])
        return

    if texto_usuario.startswith("/"):
        return

    # cache (resposta instantânea)
    chave_cache = texto_usuario.lower()
    if chave_cache in cache_respostas:
        bot.send_message(
            message.chat.id,
            cache_respostas[chave_cache],
            parse_mode="MarkdownV2"
        )
        return

    bot.send_chat_action(message.chat.id, "typing")

    instrucoes = carregar_instrucoes()

    historico = chat_sessions.get(user_id, [])
    historico_resumido = "\n".join(historico[-2:])  # bem curto

    prompt = f"""
            {instrucoes}

            Histórico recente:
            {historico_resumido}

            Usuário disse:
            {texto_usuario}
            """

    try:
        resposta = gerar_resposta(prompt)
    except RuntimeError:
        bot.send_message(
            message.chat.id,
            "⚠️ O assistente está temporariamente indisponível. Tente novamente em instantes."
        )
        return

    if not resposta:
        return

    # atualiza histórico (curto)
    historico.append(f"Usuário: {texto_usuario}")
    historico.append(f"IA: {resposta}")
    chat_sessions[user_id] = historico[-4:]

    # salva cache
    cache_respostas[chave_cache] = telegramify_markdown.markdownify(resposta)

    bot.send_message(
        message.chat.id,
        cache_respostas[chave_cache],
        parse_mode="MarkdownV2"
    )


# =========================
# Handler de post
# =========================

import io
from PIL import Image

class GeminiClient:
    IMAGE_MODELOS = [
        "gemini-3.1-flash-image-preview",
        "gemini-2.5-flash-image",
    ]

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    @staticmethod
    def _image_to_bytes(image_obj) -> bytes:
        buffer = io.BytesIO()
        image_obj.save(buffer, format="JPEG")
        return buffer.getvalue()

    @staticmethod
    def _extrair_primeira_imagem(response) -> bytes | None:
        for part in getattr(response, "parts", []) or []:
            if getattr(part, "inline_data", None) is not None:
                return GeminiClient._image_to_bytes(part.as_image())
        return None

    def generate_images(
        self,
        prompt: str,
        foto_path: str,
        n: int = 3
    ) -> list[bytes]:
        imagens_bytes: list[bytes] = []
        ultimo_erro = None

        with Image.open(foto_path) as imagem_base:
            for i in range(n):
                imagem_input = imagem_base.copy()
                gerada = False

                for modelo in self.IMAGE_MODELOS:
                    try:
                        response = self.client.models.generate_content(
                            model=modelo,
                            contents=[prompt, imagem_input],
                            config=types.GenerateContentConfig(
                                image_config=types.ImageConfig(aspect_ratio="16:9")
                            ),
                        )

                        image_bytes = self._extrair_primeira_imagem(response)
                        if not image_bytes:
                            raise RuntimeError(
                                f"Modelo {modelo} nao retornou imagem (iteracao {i + 1})."
                            )

                        imagens_bytes.append(image_bytes)
                        gerada = True
                        break
                    except Exception as e:
                        ultimo_erro = e
                        log.warning(
                            "Falha ao gerar imagem com %s na iteracao %s, tentando fallback.",
                            modelo,
                            i + 1,
                        )

                if not gerada:
                    raise RuntimeError(
                        f"Nao foi possivel gerar a imagem {i + 1} com os modelos configurados."
                    ) from ultimo_erro

        return imagens_bytes
