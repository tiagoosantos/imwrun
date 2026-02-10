import os
from google import genai
import telegramify_markdown
from config.settings import GEMINI

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTRUCOES_FILE = os.path.join(BASE_PATH, "ia", "instrucoes_gemini.txt")

# histórico por usuário
chat_sessions = {}

client = genai.Client(api_key=GEMINI)


def carregar_instrucoes():
    try:
        with open(INSTRUCOES_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


def responder_com_ia(bot, message):
    user_id = message.from_user.id
    texto_usuario = message.text

    if user_id not in chat_sessions:
        chat_sessions[user_id] = []

    historico = chat_sessions[user_id]
    instrucoes = carregar_instrucoes()

    prompt = f"""
{instrucoes}

Histórico:
{historico}

Usuário disse:
{texto_usuario}
"""

    bot.send_chat_action(message.chat.id, "typing")

    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt,
    )

    resposta = response.text.strip()

    if not resposta:
        return

    # salva histórico (curto, controlado)
    historico.append(f"Usuário: {texto_usuario}")
    historico.append(f"IA: {resposta}")

    # limita histórico para evitar explosão de tokens
    chat_sessions[user_id] = historico[-10:]

    texto_md = telegramify_markdown.markdownify(resposta)

    bot.send_message(
        message.chat.id,
        texto_md,
        parse_mode="MarkdownV2"
    )
