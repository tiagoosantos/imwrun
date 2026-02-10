import os
import time
import logging
from google import genai
from google.genai.errors import ServerError, ClientError
import telegramify_markdown
from config.settings import GEMINI

log = logging.getLogger(__name__)

# =========================
# Configurações gerais
# =========================

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTRUCOES_FILE = os.path.join(BASE_PATH, "ia", "instrucoes_gemini.txt")

# modelos em ordem de prioridade
MODELOS = [
    "gemini-3-flash-preview",  # rápido (preview, pode falhar)
    "gemini-1.5-pro",          # estável
    "gemini-1.0-pro",          # fallback final
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
    if not texto_usuario or len(texto_usuario) < 6:
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
