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


def usuario_cancelou(texto: str) -> bool:
    return texto.strip().lower() == "sair"

def parse_tempo(texto: str) -> int:
    texto = texto.strip()
    texto = texto.replace(".", ":")
    texto = texto.replace(" ", "")

    minutos, segundos = map(int, texto.split(":"))

    if segundos >= 60:
        raise ValueError("Segundos inválidos")

    return minutos * 60 + segundos

def parse_distancia(texto: str) -> int:
    """
    Aceita:
    5
    5.2
    5,2
    5.25
    5,250
    5 250
    5250

    Retorna:
    Distância em metros (int)
    """

    texto = texto.strip().lower()
    texto = texto.replace(" ", "")
    texto = texto.replace(",", ".")  # padroniza decimal

    if not texto:
        raise ValueError("Distância vazia")

    # Caso seja número inteiro grande (ex: 5250)
    if texto.isdigit():
        valor = int(texto)

        # Se for pequeno, considerar km
        if valor < 100:
            return valor * 1000

        return valor

    # Caso seja decimal (ex: 5.2 / 5.25)
    try:
        km_float = float(texto)

        if km_float <= 0:
            raise ValueError("Distância inválida")

        return int(km_float * 1000)

    except ValueError:
        raise ValueError(
            "Formato inválido. Exemplos válidos:\n"
            "5\n5.2\n5,250\n5250"
        )

def formatar_tempo(segundos: int) -> str:
    """
    Recebe segundos (int)
    Retorna MM:SS
    """

    if segundos < 0:
        raise ValueError("Tempo inválido")

    minutos = segundos // 60
    segundos_restantes = segundos % 60

    return f"{minutos:02d}:{segundos_restantes:02d}"


def formatar_distancia(distancia_metros: int) -> str:
    """
    Recebe metros (int)
    Retorna string formatada em km com 2 casas e vírgula.
    """

    if distancia_metros < 0:
        raise ValueError("Distância inválida")

    km = distancia_metros / 1000

    return f"{km:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " km"

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

    msg = bot.send_message(message.chat.id, "⏱ Informe o tempo (MM:SS)\n\nDigite 'sair' para cancelar.")
    bot.register_next_step_handler(msg, registrar_tempo, correlation_id)

def registrar_tempo(message, correlation_id):
    if not message.text:
        return

    texto = message.text.strip()

    if usuario_cancelou(texto):
        bot.send_message(message.chat.id, "❌ Registro cancelado.")
        fake_message = message
        fake_message.text = "/start"
        bot.process_new_messages([fake_message])
        return
    
    try:
        tempo_segundos = parse_tempo(texto)

        log.info(
            "Tempo informado",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "tempo_segundos": tempo_segundos,
            },
        )

        msg = bot.send_message(message.chat.id, "🏃 Distância no formato KM,metros\nEx: 5,250\n\nDigite 'sair' para cancelar.")
        bot.register_next_step_handler(msg, registrar_distancia, tempo_segundos, correlation_id)

    except Exception:
        log.warning(
            "Tempo inválido",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "valor": message.text})
        
        bot.send_message(
            message.chat.id,
            "❌ Formato inválido. Use MM:SS\n\nDigite 'sair' para cancelar.")

        bot.register_next_step_handler(
            message,
            registrar_tempo,
            correlation_id
        )

def registrar_distancia(message, tempo_segundos, correlation_id):
    if not message.text:
        return

    texto = message.text.strip()

    if usuario_cancelou(texto):
        bot.send_message(message.chat.id, "❌ Registro cancelado.")
        fake_message = message
        fake_message.text = "/start"
        bot.process_new_messages([fake_message])
        return
    
    try:
        distancia_km = parse_distancia(texto)

        log.info(
            "Distância informada",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "distancia_km": distancia_km,
            },
        )

        msg = bot.send_message(message.chat.id, "👟 Informe os passos (ou 0 se não souber)\n\nDigite 'sair' para cancelar.")
        bot.register_next_step_handler(
            msg, registrar_passos, tempo_segundos, distancia_km, correlation_id
        )

    except Exception:
        log.warning(
            "Distância inválida",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "valor": message.text,
            },
        )
        bot.send_message(message.chat.id, "❌ Distância inválida. Use KM,metros (Ex: 5,250)\n\nOu digite 'sair' para cancelar.")
        bot.register_next_step_handler(
            message,
            registrar_distancia,
            tempo_segundos,
            correlation_id
        )

def registrar_passos(message, tempo_segundos, distancia_km, correlation_id):
    if not message.text:
        return

    texto = message.text.strip()

    if usuario_cancelou(texto):
        bot.send_message(message.chat.id, "❌ Registro cancelado.")
        fake_message = message
        fake_message.text = "/start"
        bot.process_new_messages([fake_message])
        return
    
    try:
        passos = int(texto)

        log.info(
            "Passos informados",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "passos": passos,
            },
        )

        msg = bot.send_message(message.chat.id, "🔥 Informe as calorias (ou 0 se não souber)\n\nDigite 'sair' para cancelar.")
        bot.register_next_step_handler(
            msg, registrar_calorias, tempo_segundos, distancia_km, passos, correlation_id
        )

    except Exception:
        log.warning(
            "Passos inválidos",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "valor": message.text,
            },
        )
        bot.send_message(message.chat.id, "❌ Informe apenas número inteiro.\n\nDigite 'sair' para cancelar.")
        bot.register_next_step_handler(
            message,
            registrar_passos,
            tempo_segundos,
            distancia_km,
            correlation_id
        )

def registrar_calorias(message, tempo_segundos, distancia_km, passos, correlation_id):
    if not message.text:
        return

    texto = message.text.strip()

    if usuario_cancelou(texto):
        bot.send_message(message.chat.id, "❌ Registro cancelado.")
        fake_message = message
        fake_message.text = "/start"
        bot.process_new_messages([fake_message])
        return
    
    try:
        calorias = int(texto)

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
        "⏱ Informe o tempo no formato MM:SS\nEx: 45:30"
    )

    bot.register_next_step_handler(msg, pace_tempo, correlation_id)

def pace_tempo(message, correlation_id):
    texto = message.text.strip()

    if usuario_cancelou(texto):
        bot.send_message(message.chat.id, "❌ Operação cancelada.")
        fake_message = message
        fake_message.text = "/start"
        bot.process_new_messages([fake_message])
        return
    
    try:
        tempo_segundos = parse_tempo(message.text)

        log.info(
            "Tempo pace informado",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "tempo_segundos": tempo_segundos,
            },
        )

        msg = bot.send_message(
            message.chat.id,
            "🏃 Informe a distância no formato KM,metros\nEx: 5,250\n\n"
            "Ou digite 'sair' para cancelar."
        )

        bot.register_next_step_handler(
            msg,
            pace_distancia,
            tempo_segundos,
            correlation_id
        )

    except Exception:
        bot.send_message(message.chat.id, 
                            "❌ Formato inválido.\n"
                            "Use MM:SS\n"
                            "Ex: 45:30\n\n"
                            "Ou digite 'sair' para cancelar.")
        
        bot.register_next_step_handler(message, pace_tempo, correlation_id)

def pace_distancia(message, tempo_segundos, correlation_id):
    texto = message.text.strip()

    if usuario_cancelou(texto):
        bot.send_message(message.chat.id, "❌ Operação cancelada.")
        fake_message = message
        fake_message.text = "/start"
        bot.process_new_messages([fake_message])
        return

    try:
        distancia_km = parse_distancia(message.text)

        if distancia_km <= 0:
            raise ValueError

        log.info(
            "Distância pace informada",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "distancia_km": distancia_km,
            },
        )

        msg = bot.send_message(
            message.chat.id,
            "⏱ Informe o pace manual (MM:SS)\n"
            "Ou digite 0 para calcular automaticamente\n\n"
            "Ou digite 'sair' para cancelar."
        )

        bot.register_next_step_handler(
            msg,
            pace_manual,
            tempo_segundos,
            distancia_km,
            correlation_id
        )

    except Exception:
        bot.send_message(message.chat.id,
                                "❌ Formato inválido.\n"
                                "Use KM,metros\n"
                                "Ex: 5,250\n\n"
                                "Ou digite 'sair' para cancelar.")

        bot.register_next_step_handler(message, pace_distancia, tempo_segundos, correlation_id)

def pace_manual(message, tempo_segundos, distancia_km, correlation_id):
    texto = message.text.strip()

    if usuario_cancelou(texto):
        bot.send_message(message.chat.id, "❌ Operação cancelada.")
        fake_message = message
        fake_message.text = "/start"
        bot.process_new_messages([fake_message])
        return
    
    try:
        texto = message.text.strip()

        if texto == "0":
            pace_segundos = int(tempo_segundos / distancia_km)
            origem = "calculado"
        else:
            pace_segundos = parse_tempo(texto)
            origem = "manual"

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

        bot.send_message(message.chat.id,
                                "❌ Formato inválido.\n"
                                "Use MM:SS ou 0\n\n"
                                "Ou digite 'sair' para cancelar.")

        bot.register_next_step_handler(message, pace_manual, tempo_segundos, distancia_km, correlation_id)


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
