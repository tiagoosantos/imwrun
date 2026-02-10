from telebot import TeleBot, types
from datetime import datetime
import os

from config.settings import BOT_TOKEN
from service.corrida_service import CorridaService
from ia.gemini import responder_com_ia
from utils.logger_csv import configurar_monitoramento

bot = TeleBot(BOT_TOKEN)
service = CorridaService()


def iniciar_bot():
    configurar_monitoramento(bot)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Bot de Corridas iniciado...")
    bot.polling(none_stop=True, interval=1.5)


@bot.message_handler(commands=["start"])
def start(message):
    texto = (
        "🏃 *Bot de Corridas*\n\n"
        "/registrar – Registrar treino\n"
        "/pace – Calcular pace\n"
        "/ranking_km – Ranking por KM\n"
        "/ranking_tempo – Ranking por tempo\n\n"
        "💬 Fora dos comandos, posso te ajudar com dúvidas sobre corrida."
    )
    bot.send_message(message.chat.id, texto, parse_mode="Markdown")


@bot.message_handler(commands=["registrar"])
def registrar(message):
    msg = bot.send_message(message.chat.id, "⏱ Informe o tempo (minutos):")
    bot.register_next_step_handler(msg, registrar_tempo)


def registrar_tempo(message):
    try:
        tempo = int(message.text)
        msg = bot.send_message(message.chat.id, "🏃 Distância (km):")
        bot.register_next_step_handler(msg, registrar_distancia, tempo)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Valor inválido.")
        registrar(message)


def registrar_distancia(message, tempo):
    try:
        distancia = float(message.text.replace(",", "."))
        msg = bot.send_message(message.chat.id, "👣 Passos:")
        bot.register_next_step_handler(msg, registrar_passos, tempo, distancia)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Distância inválida.")


def registrar_passos(message, tempo, distancia):
    passos = int(message.text)
    msg = bot.send_message(message.chat.id, "🔥 Calorias:")
    bot.register_next_step_handler(msg, registrar_calorias, tempo, distancia, passos)


def registrar_calorias(message, tempo, distancia, passos):
    calorias = int(message.text)

    service.registrar_corrida(
        telegram_id=message.chat.id,
        nome=message.from_user.first_name,
        tempo=tempo,
        distancia=distancia,
        passos=passos,
        calorias=calorias,
    )

    bot.send_message(message.chat.id, "✅ Corrida registrada com sucesso!")


@bot.message_handler(func=lambda message: True)
def fallback_ia(message):
    if message.text.startswith("/") or message.text.lower() == "oi":
        return
    responder_com_ia(bot, message)
