from telebot import TeleBot, types
from datetime import datetime
import os

from config.settings import BOT_TOKEN
from service.corrida_service import CorridaService
from service.relatorio_service import RelatorioService
from ia.gemini import responder_com_ia
from utils.logger_csv import configurar_monitoramento

bot = TeleBot(BOT_TOKEN)

corrida_service = CorridaService()
relatorio_service = RelatorioService()


def iniciar_bot():
    configurar_monitoramento(bot)
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Bot de Corridas iniciado...")
    bot.polling(none_stop=True, interval=1.5)


# =======================
# START
# =======================

@bot.message_handler(commands=["start"])
def start(message):
    texto = (
        "🏃 *Bot de Corridas*\n\n"
        "/registrar – Registrar treino\n"
        "/pace – Calcular pace\n"
        "/ranking_km – Ranking por KM\n"
        "/ranking_km_pg <pagina> – Ranking por KM paginado\n"
        "/ranking_tempo – Ranking por tempo\n"
        "/relatorio – Relatório mensal (Excel)\n\n"
        "💬 Fora dos comandos, posso te ajudar com dúvidas sobre corrida."
    )
    bot.send_message(message.chat.id, texto, parse_mode="Markdown")


# =======================
# REGISTRO DE CORRIDA
# =======================

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
    try:
        passos = int(message.text)
        msg = bot.send_message(message.chat.id, "🔥 Calorias:")
        bot.register_next_step_handler(
            msg, registrar_calorias, tempo, distancia, passos
        )
    except ValueError:
        bot.send_message(message.chat.id, "❌ Passos inválidos.")


def registrar_calorias(message, tempo, distancia, passos):
    try:
        calorias = int(message.text)

        corrida_service.registrar_corrida(
            telegram_id=message.chat.id,
            nome=message.from_user.first_name,
            tempo=tempo,
            distancia=distancia,
            passos=passos,
            calorias=calorias,
        )

        bot.send_message(message.chat.id, "✅ Corrida registrada com sucesso!")
    except Exception:
        bot.send_message(message.chat.id, "❌ Erro ao registrar corrida.")


# =======================
# PACE
# =======================

@bot.message_handler(commands=["pace"])
def pace(message):
    msg = bot.send_message(
        message.chat.id,
        "🏃 Informe no formato:\n`tempo_em_minutos distancia_km`\n\nEx: `50 10`",
        parse_mode="Markdown",
    )
    bot.register_next_step_handler(msg, calcular_pace)


def calcular_pace(message):
    try:
        tempo, distancia = message.text.split()
        tempo = float(tempo)
        distancia = float(distancia)

        pace = round(tempo / distancia, 2)

        bot.send_message(
            message.chat.id,
            f"⏱ Pace médio: *{pace} min/km*",
            parse_mode="Markdown",
        )
    except Exception:
        bot.send_message(message.chat.id, "❌ Formato inválido.")


# =======================
# RANKINGS
# =======================

@bot.message_handler(commands=["ranking_km"])
def ranking_km(message):
    ranking = corrida_service.repo.ranking_km(limit=10)

    if not ranking:
        bot.send_message(message.chat.id, "📭 Nenhuma corrida registrada ainda.")
        return

    texto = "🏆 *Ranking por Quilometragem*\n\n"
    for pos, (_, nome, total_km) in enumerate(ranking, start=1):
        texto += f"{pos}º - {nome}: {total_km} km\n"

    bot.send_message(message.chat.id, texto, parse_mode="Markdown")


@bot.message_handler(regexp=r"^/ranking_km_pg\s+\d+$")
def ranking_km_pg(message):
    pagina = int(message.text.split()[1])
    limit = 10
    offset = (pagina - 1) * limit

    ranking = corrida_service.repo.ranking_km(limit=limit + offset)
    ranking = ranking[offset:]

    if not ranking:
        bot.send_message(message.chat.id, "📭 Página vazia.")
        return

    texto = f"🏆 *Ranking por KM – Página {pagina}*\n\n"
    for pos, (_, nome, total_km) in enumerate(
        ranking, start=offset + 1
    ):
        texto += f"{pos}º - {nome}: {total_km} km\n"

    bot.send_message(message.chat.id, texto, parse_mode="Markdown")


@bot.message_handler(commands=["ranking_tempo"])
def ranking_tempo(message):
    ranking = corrida_service.repo.ranking_tempo(limit=10)

    if not ranking:
        bot.send_message(message.chat.id, "📭 Nenhuma corrida registrada ainda.")
        return

    texto = "⏱ *Ranking por Tempo Total*\n\n"
    for pos, (_, nome, tempo_total) in enumerate(ranking, start=1):
        texto += f"{pos}º - {nome}: {tempo_total} min\n"

    bot.send_message(message.chat.id, texto, parse_mode="Markdown")


# =======================
# RELATÓRIO (OPCIONAL)
# =======================

@bot.message_handler(commands=["relatorio"])
def relatorio(message):
    msg = bot.send_message(
        message.chat.id,
        "📊 Informe o mês no formato YYYY-MM\nEx: 2026-01"
    )
    bot.register_next_step_handler(msg, gerar_relatorio)


def gerar_relatorio(message):
    try:
        arquivo = relatorio_service.gerar_relatorio_mensal(message.text)

        with open(arquivo, "rb") as f:
            bot.send_document(message.chat.id, f)

    except Exception:
        bot.send_message(message.chat.id, "❌ Erro ao gerar relatório.")


# =======================
# FALLBACK IA
# =======================

@bot.message_handler(func=lambda message: True)
def fallback_ia(message):
    if message.text.startswith("/") or message.text.lower() == "oi":
        return
    responder_com_ia(bot, message)
