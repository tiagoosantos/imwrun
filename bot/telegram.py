from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.settings import BOT_TOKEN
from service.corrida_service import CorridaService
from service.usuario_service import UsuarioService
from service.relatorio_service import RelatorioService
from ia.gemini import responder_com_ia

# =======================
# LOGGING – PADRÃO CRUE
# =======================

from utils.logging.log_config import HandlerConfig

APP_NAME = "Runner"
SETOR_NAME = "IMW"
APP = f"{SETOR_NAME}_{APP_NAME}"

log_config = HandlerConfig(APP, email="gmail", long_running=True)
log, email_handler = log_config.get_logger(APP)

# =======================
# BOT / SERVICES
# =======================

bot = TeleBot(BOT_TOKEN)

corrida_service = CorridaService()
usuario_service = UsuarioService()
relatorio_service = RelatorioService()

# =======================
# INIT
# =======================

def iniciar_bot():
    log.info("Bot Runner iniciado")
    bot.polling(none_stop=True, interval=1.5)

# =======================
# /START
# =======================

@bot.message_handler(commands=["start"])
def start(message):
    correlation_id = message.message_id
    telegram_id = message.from_user.id
    nome = message.from_user.first_name or "Usuário"

    usuario_service.registrar_usuario(
        telegram_id=telegram_id,
        nome=nome,
    )

    log.info(
        "Comando /start",
        extra={
            "telegram_id": telegram_id,
            "correlation_id": correlation_id,
            "command": "/start",
        },
    )

    texto = (
        "🏃 *Bem-vindo ao IMW Runner!*\n\n"
        "Aqui você registra treinos e acompanha rankings de corrida.\n\n"
        "*Escolha uma ação:*"
    )

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🏃 Registrar treino", callback_data="cmd_registrar"),
        InlineKeyboardButton("🏆 Ranking por KM", callback_data="cmd_ranking_km"),
        InlineKeyboardButton("⏱ Calcular pace", callback_data="cmd_pace"),
        InlineKeyboardButton("📄 Relatório mensal", callback_data="cmd_relatorio"),
    )

    bot.send_message(
        message.chat.id,
        texto,
        reply_markup=markup,
        parse_mode="Markdown",
    )

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    bot.answer_callback_query(call.id)

    chat_id = call.message.chat.id
    user = call.from_user

    comandos = {
        "cmd_registrar": "/registrar",
        "cmd_ranking_km": "/ranking_km",
        "cmd_pace": "/pace",
        "cmd_relatorio": "/relatorio",
    }

    comando = comandos.get(call.data)
    if not comando:
        return

    # cria uma mensagem "fake" com o comando
    fake_message = call.message
    fake_message.text = comando
    fake_message.from_user = user
    fake_message.chat = call.message.chat

    # processa como se o usuário tivesse digitado
    bot.process_new_messages([fake_message])


# =======================
# REGISTRO DE CORRIDA
# =======================

@bot.message_handler(commands=["registrar"])
def registrar(message):
    correlation_id = message.message_id

    log.info(
        "Início registro de corrida",
        extra={
            "telegram_id": message.chat.id,
            "correlation_id": correlation_id,
            "command": "/registrar",
        },
    )

    msg = bot.send_message(message.chat.id, "⏱ Informe o tempo (minutos):")
    bot.register_next_step_handler(msg, registrar_tempo, correlation_id)

def registrar_tempo(message, correlation_id):
    try:
        tempo = int(message.text)

        log.info(
            "Tempo informado",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "tempo": tempo,
            },
        )

        msg = bot.send_message(message.chat.id, "🏃 Distância (km):")
        bot.register_next_step_handler(msg, registrar_distancia, tempo, correlation_id)

    except ValueError:
        log.warning(
            "Tempo inválido",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "valor": message.text,
            },
        )
        bot.send_message(message.chat.id, "❌ Tempo inválido.")

def registrar_distancia(message, tempo, correlation_id):
    try:
        distancia = float(message.text.replace(",", "."))

        log.info(
            "Distância informada",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "distancia": distancia,
            },
        )

        msg = bot.send_message(message.chat.id, "👣 Passos:")
        bot.register_next_step_handler(
            msg, registrar_passos, tempo, distancia, correlation_id
        )

    except ValueError:
        log.warning(
            "Distância inválida",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "valor": message.text,
            },
        )
        bot.send_message(message.chat.id, "❌ Distância inválida.")

def registrar_passos(message, tempo, distancia, correlation_id):
    try:
        passos = int(message.text)

        log.info(
            "Passos informados",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "passos": passos,
            },
        )

        msg = bot.send_message(message.chat.id, "🔥 Calorias:")
        bot.register_next_step_handler(
            msg, registrar_calorias, tempo, distancia, passos, correlation_id
        )

    except ValueError:
        log.warning(
            "Passos inválidos",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "valor": message.text,
            },
        )
        bot.send_message(message.chat.id, "❌ Passos inválidos.")

def registrar_calorias(message, tempo, distancia, passos, correlation_id):
    try:
        calorias = int(message.text)

        corrida_service.registrar_corrida(
            telegram_id=message.chat.id,
            tempo_minutos=tempo,
            distancia_km=distancia,
            passos=passos,
            calorias=calorias,
        )

        log.info(
            "Corrida registrada com sucesso",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "tempo": tempo,
                "distancia": distancia,
            },
        )

        bot.send_message(message.chat.id, "✅ Corrida registrada!")

    except Exception:
        log.exception(
            "Erro ao registrar corrida",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
            },
        )
        bot.send_message(message.chat.id, "❌ Erro ao registrar corrida.")

# =======================
# PACE
# =======================

@bot.message_handler(commands=["pace"])
def pace(message):
    correlation_id = message.message_id

    log.info(
        "Comando /pace",
        extra={
            "telegram_id": message.chat.id,
            "correlation_id": correlation_id,
        },
    )

    msg = bot.send_message(
        message.chat.id,
        "Informe no formato:\n`tempo_em_minutos distancia_km`\nEx: `50 10`",
        parse_mode="Markdown",
    )
    bot.register_next_step_handler(msg, calcular_pace, correlation_id)

def calcular_pace(message, correlation_id):
    try:
        tempo, distancia = message.text.split()
        pace = round(float(tempo) / float(distancia), 2)

        log.info(
            "Pace calculado",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "pace": pace,
            },
        )

        bot.send_message(
            message.chat.id,
            f"⏱ Pace médio: *{pace} min/km*",
            parse_mode="Markdown",
        )
    except Exception:
        log.warning(
            "Erro cálculo pace",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "valor": message.text,
            },
        )
        bot.send_message(message.chat.id, "❌ Formato inválido.")

# =======================
# RANKINGS
# =======================

@bot.message_handler(commands=["ranking_km"])
def ranking_km(message):
    correlation_id = message.message_id

    log.info(
        "Ranking KM solicitado",
        extra={
            "telegram_id": message.chat.id,
            "correlation_id": correlation_id,
        },
    )

    ranking = corrida_service.repo.ranking_km(limit=10)
    if not ranking:
        bot.send_message(message.chat.id, "📭 Nenhuma corrida registrada.")
        return

    texto = "🏆 *Ranking por KM*\n\n"
    for pos, (_, nome, total_km) in enumerate(ranking, start=1):
        texto += f"{pos}º - {nome}: {total_km} km\n"

    bot.send_message(message.chat.id, texto, parse_mode="Markdown")

@bot.message_handler(regexp=r"^/ranking_km_pg\s+\d+$")
def ranking_km_pg(message):
    correlation_id = message.message_id
    pagina = int(message.text.split()[1])

    limit = 10
    offset = (pagina - 1) * limit

    log.info(
        "Ranking KM paginado solicitado",
        extra={
            "telegram_id": message.chat.id,
            "correlation_id": correlation_id,
            "pagina": pagina,
        },
    )

    ranking = corrida_service.repo.ranking_km(limit=limit + offset)[offset:]
    if not ranking:
        bot.send_message(message.chat.id, "📭 Página vazia.")
        return

    texto = f"🏆 *Ranking por KM – Página {pagina}*\n\n"
    for pos, (_, nome, total_km) in enumerate(ranking, start=offset + 1):
        texto += f"{pos}º - {nome}: {total_km} km\n"

    bot.send_message(message.chat.id, texto, parse_mode="Markdown")

@bot.message_handler(commands=["ranking_tempo"])
def ranking_tempo(message):
    correlation_id = message.message_id

    log.info(
        "Ranking tempo solicitado",
        extra={
            "telegram_id": message.chat.id,
            "correlation_id": correlation_id,
        },
    )

    ranking = corrida_service.repo.ranking_tempo(limit=10)
    if not ranking:
        bot.send_message(message.chat.id, "📭 Nenhuma corrida registrada.")
        return

    texto = "⏱ *Ranking por Tempo*\n\n"
    for pos, (_, nome, tempo_total) in enumerate(ranking, start=1):
        texto += f"{pos}º - {nome}: {tempo_total} min\n"

    bot.send_message(message.chat.id, texto, parse_mode="Markdown")

# =======================
# RELATÓRIO
# =======================

@bot.message_handler(commands=["relatorio"])
def relatorio(message):
    correlation_id = message.message_id

    log.info(
        "Relatório solicitado",
        extra={
            "telegram_id": message.chat.id,
            "correlation_id": correlation_id,
        },
    )

    msg = bot.send_message(
        message.chat.id,
        "Informe o mês no formato YYYY-MM\nEx: 2026-01"
    )
    bot.register_next_step_handler(msg, gerar_relatorio, correlation_id)

def gerar_relatorio(message, correlation_id):
    try:
        arquivo = relatorio_service.gerar_relatorio_mensal(message.text)

        log.info(
            "Relatório gerado",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "mes": message.text,
            },
        )

        with open(arquivo, "rb") as f:
            bot.send_document(message.chat.id, f)

    except Exception:
        log.exception(
            "Erro ao gerar relatório",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
            },
        )
        bot.send_message(message.chat.id, "❌ Erro ao gerar relatório.")

# =======================
# FALLBACK IA
# =======================

@bot.message_handler(
    func=lambda m: (
        m.text
        and not m.text.startswith("/")
    )
)
def fallback_ia(message):
    responder_com_ia(bot, message)
