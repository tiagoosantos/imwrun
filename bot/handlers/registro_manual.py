from bot.state.registro_state import registro_temp, limpar_sessao
from bot.utils.bot_utils import usuario_cancelou, parse_tempo, parse_distancia
from bot.keyboards.registro_keyboard import teclado_tipo
from bot.utils.timeout_manager import iniciar_timeout, cancelar_timeout


def iniciar_registro_manual(bot, services, message):
    log = services["log"]
    correlation_id = message.message_id

    log.info(
        "Início registro manual",
        extra={
            "telegram_id": message.chat.id,
            "correlation_id": correlation_id,
        },
    )

    msg = bot.send_message(
        message.chat.id,
        "⏱ Informe o tempo (MM:SS)\n\nDigite 'sair' para cancelar."
    )
    iniciar_timeout(bot, message.chat.id)

    bot.register_next_step_handler(
        msg,
        lambda m: registrar_tempo(bot, services, m, correlation_id)
    )


def registrar_tempo(bot, services, message, correlation_id):
    log = services["log"]
    correlation_id = correlation_id
    cancelar_timeout(message.chat.id)

    log.info(
        "Registrando tempo",
        extra={
            "telegram_id": message.chat.id,
            "correlation_id": correlation_id,
        },
    )

    texto = message.text.strip()

    if usuario_cancelou(texto):
        limpar_sessao(message.chat.id)
        bot.send_message(message.chat.id, "❌ Registro cancelado.")
        log.info(
            "Registro cancelado via texto",
            extra={"telegram_id": message.chat.id, "correlation_id": correlation_id}
        )
        return

    try:
        tempo_segundos = parse_tempo(texto)

        log.info(
            "Tempo informado",
            extra={
                "telegram_id": message.chat.id,
                "tempo_segundos": tempo_segundos,
                "correlation_id": correlation_id
            },
        )

        msg = bot.send_message(
            message.chat.id,
            "🏃 Distância (KM,metros)\nEx: 5,250"
        )
        iniciar_timeout(bot, message.chat.id)

        bot.register_next_step_handler(
            msg,
            lambda m: registrar_distancia(
                bot, services, m, tempo_segundos, correlation_id
            )
        )

    except Exception:
        log.warning("Tempo inválido")
        bot.send_message(message.chat.id, "❌ Formato inválido. Use MM:SS")
        bot.register_next_step_handler(
            message,
            lambda m: registrar_tempo(bot, services, m, correlation_id)
        )


def registrar_distancia(bot, services, message, tempo_segundos, correlation_id):
    log = services["log"]
    correlation_id = correlation_id
    cancelar_timeout(message.chat.id)

    log.info(
        "Registrando distância",
        extra={
            "telegram_id": message.chat.id,
            "tempo_segundos": tempo_segundos,
            "correlation_id": correlation_id
        },
    )

    texto = message.text.strip()

    if usuario_cancelou(texto):
        limpar_sessao(message.chat.id)
        bot.send_message(message.chat.id, "❌ Registro cancelado.")
        log.info(
            "Registro cancelado via texto",
            extra={"telegram_id": message.chat.id, "correlation_id": correlation_id}
        )
        return

    try:
        distancia_metros = parse_distancia(texto)

        msg = bot.send_message(
            message.chat.id,
            "👟 Informe os passos (ou 0 se não souber)"
        )
        iniciar_timeout(bot, message.chat.id)

        bot.register_next_step_handler(
            msg,
            lambda m: registrar_passos(
                bot,
                services,
                m,
                tempo_segundos,
                distancia_metros,
                correlation_id
            )
        )

    except Exception:
        log.warning("Distância inválida")
        bot.send_message(message.chat.id, "❌ Distância inválida")
        bot.register_next_step_handler(
            message,
            lambda m: registrar_distancia(
                bot, services, m, tempo_segundos, correlation_id
            )
        )


def registrar_passos(bot, services, message, tempo_segundos, distancia_metros, correlation_id):
    log = services["log"]
    correlation_id = correlation_id
    cancelar_timeout(message.chat.id)

    log.info(
        "Registrando passos",
        extra={
            "telegram_id": message.chat.id,
            "tempo_segundos": tempo_segundos,
            "distancia_metros": distancia_metros,
            "correlation_id": correlation_id
        },
    )

    texto = message.text.strip()

    if usuario_cancelou(texto):
        limpar_sessao(message.chat.id)
        bot.send_message(message.chat.id, "❌ Registro cancelado.")
        log.info(
            "Registro cancelado via texto",
            extra={"telegram_id": message.chat.id, "correlation_id": correlation_id}
        )
        return

    try:
        passos = int(texto)

        msg = bot.send_message(
            message.chat.id,
            "🔥 Informe as calorias (ou 0 se não souber)"
        )
        iniciar_timeout(bot, message.chat.id)

        bot.register_next_step_handler(
            msg,
            lambda m: registrar_calorias(
                bot,
                services,
                m,
                tempo_segundos,
                distancia_metros,
                passos,
                correlation_id
            )
        )

    except Exception:
        log.warning("Passos inválidos")
        bot.send_message(message.chat.id, "❌ Informe apenas número inteiro")
        bot.register_next_step_handler(
            message,
            lambda m: registrar_passos(
                bot,
                services,
                m,
                tempo_segundos,
                distancia_metros,
                correlation_id
            )
        )


def registrar_calorias(bot, services, message, tempo_segundos, distancia_metros, passos, correlation_id):
    log = services["log"]
    correlation_id = correlation_id
    cancelar_timeout(message.chat.id)

    log.info(
        "Registrando calorias",
        extra={
            "telegram_id": message.chat.id,
            "tempo_segundos": tempo_segundos,
            "distancia_metros": distancia_metros,
            "passos": passos,
            "correlation_id": correlation_id
        },
    )

    texto = message.text.strip()

    if usuario_cancelou(texto):
        limpar_sessao(message.chat.id)
        bot.send_message(message.chat.id, "❌ Registro cancelado.")
        log.info(
            "Registro cancelado via texto",
            extra={"telegram_id": message.chat.id, "correlation_id": correlation_id}
        )
        return

    try:
        calorias = int(texto)

        registro_temp[message.chat.id] = {
            "tempo_segundos": tempo_segundos,
            "distancia_metros": distancia_metros,
            "passos": passos,
            "calorias": calorias,
            "correlation_id": correlation_id,
        }

        bot.send_message(
            message.chat.id,
            "🏷 Qual o tipo do treino?",
            reply_markup=teclado_tipo()
        )
        iniciar_timeout(bot, message.chat.id)

    except Exception:
        log.warning("Calorias inválidas")
        bot.send_message(message.chat.id, "❌ Informe apenas número inteiro")
        bot.register_next_step_handler(
            message,
            lambda m: registrar_calorias(
                bot,
                services,
                m,
                tempo_segundos,
                distancia_metros,
                passos,
                correlation_id
            )
        )