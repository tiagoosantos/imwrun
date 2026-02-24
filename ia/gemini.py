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


class GeminiClient:

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    # ======================================================
    # GERAÇÃO DE IMAGENS PARA POST (3 variações)
    # ======================================================

    def generate_images(
        self,
        prompt: str,
        images: list[str],
        n: int = 3,
        size: str = "1080x1920"
    ) -> list[bytes]:

        """
        prompt: texto final já montado pelo PostService
        images: lista de imagens em base64 (sem header data:image/...)
        n: quantidade de imagens a gerar
        size: resolução desejada (vertical)
        """

        contents = []

        # 🔹 Adicionar imagens enviadas pelo usuário
        for img_base64 in images:
            contents.append(
                types.Part.from_bytes(
                    data=base64.b64decode(img_base64),
                    mime_type="image/jpeg"
                )
            )

        # 🔹 Adicionar instrução textual forte
        prompt_final = f"""
        {prompt}

        Gere exatamente {n} imagens diferentes.
        Formato obrigatório: {size}.
        Orientação vertical.
        Cada imagem deve ter layout diferente.
        Não gere texto explicativo fora das imagens.
        """

        contents.append(prompt_final)

        # 🔹 Chamada ao Gemini
        response = self.client.models.generate_content(
            model="gemini-2.0-flash-exp",  # modelo multimodal rápido
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=["IMAGE"]
            )
        )

        imagens_bytes = []

        # 🔹 Extrair imagens retornadas
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if part.inline_data:
                    imagens_bytes.append(
                        base64.b64decode(part.inline_data.data)
                    )

        # Segurança: garantir 3 outputs
        if len(imagens_bytes) < n:
            raise Exception("Gemini não retornou imagens suficientes.")

        return imagens_bytes[:n]