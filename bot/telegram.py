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

@bot.callback_query_handler(func=lambda call: call.data.startswith("ranking_km_"))
def callback_ranking_km(call):
    bot.answer_callback_query(call.id)

    correlation_id = call.message.message_id
    chat_id = call.message.chat.id

    pagina = int(call.data.split("_")[-1])

    enviar_ranking_km(chat_id, pagina, correlation_id)


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
        minutos, segundos = map(int, message.text.split(":"))
        tempo_segundos = minutos * 60 + segundos

        log.info(
            "Tempo informado",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "tempo_segundos": tempo_segundos,
            },
        )

        msg = bot.send_message(message.chat.id, "🏃 Distância no formato KM,metros\nEx: 5,250")
        bot.register_next_step_handler(msg, registrar_distancia, tempo_segundos, correlation_id)

    except ValueError:
        log.warning(
            "Tempo inválido",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "valor": message.text,
            },
        )
        bot.send_message(message.chat.id, "❌ Tempo inválido. Use o formato MM:SS, ex: 50:30")

def registrar_distancia(message, tempo_segundos, correlation_id):
    try:
        km, metros = message.text.split(",")
        distancia_km = int(km) + (int(metros) / 1000)

        log.info(
            "Distância informada",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "distancia_km": distancia_km,
            },
        )

        msg = bot.send_message(message.chat.id, "👣 Passos:")
        bot.register_next_step_handler(
            msg, registrar_passos, tempo_segundos, distancia_km, correlation_id
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
        bot.send_message(message.chat.id, "❌ Distância inválida. Use KM,metros (Ex: 5,250)")

def registrar_passos(message, tempo_segundos, distancia_km, correlation_id):
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
            msg, registrar_calorias, tempo_segundos, distancia_km, passos, correlation_id
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

def registrar_calorias(message, tempo_segundos, distancia_km, passos, correlation_id):
    try:
        calorias = int(message.text)

        corrida_service.registrar_corrida(
            telegram_id=message.chat.id,
            tempo_minutos=tempo_segundos,
            distancia_km=distancia_km,
            passos=passos,
            calorias=calorias,
        )

        log.info(
            "Corrida registrada com sucesso",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "tempo": tempo_segundos/60,
                "distancia_km": distancia_km,
                "passos": passos,
                "calorias": calorias},
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

# @bot.message_handler(commands=["pace"])
# def pace(message):
#     correlation_id = message.message_id

#     log.info(
#         "Comando /pace",
#         extra={
#             "telegram_id": message.chat.id,
#             "correlation_id": correlation_id,
#         },
#     )

#     msg = bot.send_message(
#         message.chat.id,
#         "Informe no formato:\n`tempo_em_minutos distancia_km`\nEx: `50 10`",
#         parse_mode="Markdown",
#     )
#     bot.register_next_step_handler(msg, calcular_pace, correlation_id)


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
        "Informe:\n"
        "Tempo (MM:SS)\n"
        "Distância (KM,metros)\n"
        "Opcional: Pace manual (MM:SS)\n\n"
        "Exemplo:\n45:30\n5,000\n0"
    )

    bot.register_next_step_handler(msg, calcular_pace, correlation_id)


def calcular_pace(message, correlation_id):
    try:
        linhas = [l.strip() for l in message.text.strip().split("\n") if l.strip()]

        if len(linhas) < 2:
            raise ValueError("Dados insuficientes")

        tempo_str = linhas[0]
        distancia_str = linhas[1]

        # =========================
        # TEMPO → SEGUNDOS
        # =========================
        minutos, segundos = map(int, tempo_str.split(":"))

        if segundos >= 60:
            raise ValueError("Segundos inválidos")

        tempo_segundos = minutos * 60 + segundos

        # =========================
        # DISTÂNCIA → KM
        # =========================
        km, metros = distancia_str.split(",")

        if int(metros) >= 1000:
            raise ValueError("Metros inválidos")

        distancia_km = int(km) + (int(metros) / 1000)

        if distancia_km <= 0:
            raise ValueError("Distância inválida")

        # =========================
        # PACE
        # =========================
        if len(linhas) == 3:
            # pace manual informado
            pace_manual_str = linhas[2]

            m, s = map(int, pace_manual_str.split(":"))

            if s >= 60:
                raise ValueError("Segundos do pace inválidos")

            pace_segundos = m * 60 + s

            origem = "manual"
        else:
            # calcular automaticamente
            pace_segundos = int(tempo_segundos / distancia_km)
            origem = "calculado"

        minutos_final = pace_segundos // 60
        segundos_final = pace_segundos % 60

        pace_formatado = f'{minutos_final:02d}"{segundos_final:02d}\''

        log.info(
            "Pace processado",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "tempo_segundos": tempo_segundos,
                "distancia_km": distancia_km,
                "pace_segundos": pace_segundos,
                "origem": origem,
            },
        )

        bot.send_message(
            message.chat.id,
            f"⏱ Seu pace é: *{pace_formatado} por km*",
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

        bot.send_message(
            message.chat.id,
            "❌ Formato inválido.\n\n"
            "Use:\n"
            "45:30\n"
            "5,000\n"
            "Opcional: 4:33"
        )



# =======================
# RANKINGS
# =======================

# @bot.message_handler(commands=["ranking_km"])
# def ranking_km(message):
#     correlation_id = message.message_id

#     log.info(
#         "Ranking KM solicitado",
#         extra={
#             "telegram_id": message.chat.id,
#             "correlation_id": correlation_id,
#         },
#     )

#     ranking = corrida_service.repo.ranking_km(limit=10)
#     if not ranking:
#         bot.send_message(message.chat.id, "📭 Nenhuma corrida registrada.")
#         return

#     texto = "🏆 *Ranking por KM*\n\n"
#     for pos, (_, nome, total_km) in enumerate(ranking, start=1):
#         texto += f"{pos}º - {nome}: {float(total_km):.2f} km\n"

#     bot.send_message(message.chat.id, texto, parse_mode="Markdown")


# @bot.message_handler(regexp=r"^/ranking_km_pg\s+\d+$")
# def ranking_km_pg(message):
@bot.message_handler(commands=["ranking_km"])
def ranking_km(message):
    correlation_id = message.message_id
    pagina = 1
    enviar_ranking_km(message.chat.id, pagina, correlation_id)


def enviar_ranking_km(chat_id, pagina, correlation_id):
    limit = 10
    offset = (pagina - 1) * limit

    log.info(
        "Ranking KM solicitado",
        extra={
            "telegram_id": chat_id,
            "correlation_id": correlation_id,
            "pagina": pagina,
        },
    )

    ranking = corrida_service.repo.ranking_km(limit=limit + offset)
    ranking = ranking[offset:]

    if not ranking:
        bot.send_message(chat_id, "📭 Página vazia.")
        return

    texto = f"🏆 *Ranking por KM – Página {pagina}*\n\n"

    for pos, (_, nome, total_km) in enumerate(ranking, start=offset + 1):
        texto += f"{pos}º - {nome}: {float(total_km):.2f} km\n"

    # ===== BOTÕES =====
    markup = InlineKeyboardMarkup(row_width=2)

    botoes = []

    if pagina > 1:
        botoes.append(
            InlineKeyboardButton(
                "⬅ Anterior",
                callback_data=f"ranking_km_{pagina-1}"
            )
        )

    if len(ranking) == limit:
        botoes.append(
            InlineKeyboardButton(
                "➡ Próxima",
                callback_data=f"ranking_km_{pagina+1}"
            )
        )

    if botoes:
        markup.add(*botoes)

    bot.send_message(
        chat_id,
        texto,
        reply_markup=markup if botoes else None,
        parse_mode="Markdown"
    )


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
        minutos = tempo_total // 60
        segundos = tempo_total % 60
        texto += f"{pos}º - {nome}: {minutos:02d}:{segundos:02d}\n"

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
    func=lambda m: (m.text and not m.text.startswith("/")))

def fallback_ia(message):
    responder_com_ia(bot, message)
