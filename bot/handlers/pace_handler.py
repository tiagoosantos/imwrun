from bot.utils.bot_utils import (
    usuario_cancelou,
    parse_tempo,
    parse_distancia,
)


# ==========================================================
# FUNÇÃO PRINCIPAL REUTILIZÁVEL
# ==========================================================

def pace_command(bot, services, message):

    log = services["log"]
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
        "⏱ Informe o tempo no formato MM:SS\n"
        "Ex: 45:30\n\n"
        "Digite 'sair' para cancelar."
    )

    bot.register_next_step_handler(
        msg,
        lambda m: pace_tempo(bot, services, m, correlation_id)
    )


# ==========================================================
# REGISTRO DO COMANDO
# ==========================================================

def register_pace(bot, services):

    @bot.message_handler(commands=["pace"])
    def pace(message):
        pace_command(bot, services, message)


# ==========================================================
# TEMPO
# ==========================================================

def pace_tempo(bot, services, message, correlation_id):

    log = services["log"]

    if not message.text:
        return

    texto = message.text.strip()

    if usuario_cancelou(texto):
        bot.send_message(message.chat.id, "❌ Operação cancelada.")
        return

    try:

        tempo_segundos = parse_tempo(texto)

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
            "🏃 Informe a distância no formato KM,metros\n"
            "Ex: 5,250\n\n"
            "Digite 'sair' para cancelar."
        )

        bot.register_next_step_handler(
            msg,
            lambda m: pace_distancia(
                bot,
                services,
                m,
                tempo_segundos,
                correlation_id
            )
        )

    except Exception:

        log.warning(
            "Tempo pace inválido",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "valor": message.text,
            },
        )

        msg = bot.send_message(
            message.chat.id,
            "❌ Formato inválido.\n"
            "Use MM:SS\n"
            "Ex: 45:30\n\n"
            "Digite 'sair' para cancelar."
        )

        bot.register_next_step_handler(
            msg,
            lambda m: pace_tempo(bot, services, m, correlation_id)
        )


# ==========================================================
# DISTÂNCIA
# ==========================================================

def pace_distancia(bot, services, message, tempo_segundos, correlation_id):

    log = services["log"]

    if not message.text:
        return

    texto = message.text.strip()

    if usuario_cancelou(texto):
        bot.send_message(message.chat.id, "❌ Operação cancelada.")
        return

    try:

        distancia_metros = parse_distancia(texto)

        if distancia_metros <= 0:
            raise ValueError

        log.info(
            "Distância pace informada",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "distancia_metros": distancia_metros,
            },
        )

        msg = bot.send_message(
            message.chat.id,
            "⏱ Informe o pace manual (MM:SS)\n"
            "Ou digite 0 para calcular automaticamente\n\n"
            "Digite 'sair' para cancelar."
        )

        bot.register_next_step_handler(
            msg,
            lambda m: pace_manual(
                bot,
                services,
                m,
                tempo_segundos,
                distancia_metros,
                correlation_id
            )
        )

    except Exception:

        log.warning(
            "Distância pace inválida",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
                "valor": message.text,
            },
        )

        msg = bot.send_message(
            message.chat.id,
            "❌ Formato inválido.\n"
            "Use KM,metros\n"
            "Ex: 5,250\n\n"
            "Digite 'sair' para cancelar."
        )

        bot.register_next_step_handler(
            msg,
            lambda m: pace_distancia(
                bot,
                services,
                m,
                tempo_segundos,
                correlation_id
            )
        )


# ==========================================================
# PACE FINAL
# ==========================================================

def pace_manual(bot, services, message, tempo_segundos, distancia_metros, correlation_id):

    log = services["log"]

    if not message.text:
        return

    texto = message.text.strip()

    if usuario_cancelou(texto):
        bot.send_message(message.chat.id, "❌ Operação cancelada.")
        return

    try:

        if texto == "0":
            distancia_km = distancia_metros / 1000
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
                "distancia_metros": distancia_metros,
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

        msg = bot.send_message(
            message.chat.id,
            "❌ Formato inválido.\n"
            "Use MM:SS ou 0\n\n"
            "Digite 'sair' para cancelar."
        )

        bot.register_next_step_handler(
            msg,
            lambda m: pace_manual(
                bot,
                services,
                m,
                tempo_segundos,
                distancia_metros,
                correlation_id
            )
        )
