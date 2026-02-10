import os
import google.generativeai as genai
import telegramify_markdown
from config.settings import GEMINI

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTRUCOES_FILE = os.path.join(BASE_PATH, "instrucoes_gemini.txt")

chat_sessions = {}


def carregar_instrucoes():
    try:
        with open(INSTRUCOES_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""


genai.configure(api_key=GEMINI)

model = genai.GenerativeModel(
    "gemini-3-flash-preview",
    system_instruction=carregar_instrucoes(),
)


def responder_com_ia(bot, message):
    user_id = message.from_user.id

    if user_id not in chat_sessions:
        chat_sessions[user_id] = model.start_chat(history=[])

    chat = chat_sessions[user_id]
    bot.send_chat_action(message.chat.id, "typing")

    response = chat.send_message(message.text)
    texto = telegramify_markdown.markdownify(response.text)

    bot.send_message(message.chat.id, texto, parse_mode="MarkdownV2")
