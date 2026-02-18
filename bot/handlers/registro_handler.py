from bot.state.registro_state import registro_temp, limpar_sessao
from bot.keyboards.registro_keyboard import (
    teclado_tipo,
    teclado_local,
    teclado_confirmacao
)
from bot.utils.bot_utils import (
    usuario_cancelou,
    parse_tempo,
    parse_distancia,
    formatar_tempo,
    formatar_distancia
)


# ==========================================================
# FUNÇÃO REUTILIZÁVEL
# ==========================================================

def registrar_command(bot, services, message):

    log = services["log"]
    correlation_id = message.message_id

    log.info(
        "Início registro de corrida",
        extra={
            "telegram_id": message.chat.id,
            "correlation_id": correlation_id,
        },
    )

    msg = bot.send_message(
        message.chat.id,
        "⏱ Informe o tempo (MM:SS)\n\nDigite 'sair' para cancelar."
    )

    bot.register_next_step_handler(
        msg,
        lambda m: registrar_tempo(bot, services, m, correlation_id)
    )


# ==========================================================
# HANDLER REGISTRO
# ==========================================================

def register_registro(bot, services):

    @bot.message_handler(commands=["registrar"])
    def registrar(message):
        registrar_command(bot, services, message)

    # CALLBACK TIPO
    @bot.callback_query_handler(func=lambda call: call.data.startswith("tipo_"))
    def callback_tipo(call):

        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id
        log = services["log"]

        if chat_id not in registro_temp:
            log.warning("Sessão expirada no tipo")
            bot.send_message(chat_id, "❌ Sessão expirada.")
            return

        tipo = call.data.replace("tipo_", "")
        registro_temp[chat_id]["tipo_treino"] = tipo

        log.info(
            "Tipo selecionado",
            extra={
                "telegram_id": chat_id,
                "tipo_treino": tipo,
            },
        )

        bot.send_message(
            chat_id,
            "📍 Onde foi realizado o treino?",
            reply_markup=teclado_local()
        )

    # CALLBACK LOCAL
    @bot.callback_query_handler(func=lambda call: call.data.startswith("local_"))
    def callback_local(call):

        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id
        log = services["log"]
        dados = registro_temp.get(chat_id)

        if not dados:
            log.warning("Sessão expirada no local")
            bot.send_message(chat_id, "❌ Sessão expirada.")
            return

        local = call.data.replace("local_", "")
        dados["local_treino"] = local

        tempo_formatado = formatar_tempo(dados["tempo_segundos"])
        distancia_formatada = formatar_distancia(dados["distancia_metros"])

        resumo = (
            "📋 *Resumo do treino*\n\n"
            f"⏱ Tempo: {tempo_formatado}\n"
            f"📏 Distância: {distancia_formatada}\n"
            f"👟 Passos: {dados['passos']}\n"
            f"🔥 Calorias: {dados['calorias']}\n"
            f"🏷 Tipo: {dados['tipo_treino']}\n"
            f"📍 Local: {dados['local_treino']}\n\n"
            "Confirmar registro?"
        )

        bot.send_message(
            chat_id,
            resumo,
            reply_markup=teclado_confirmacao(),
            parse_mode="Markdown"
        )

    # CALLBACK CONFIRMAR
    @bot.callback_query_handler(func=lambda call: call.data == "confirmar_registro")
    def callback_confirmar(call):

        bot.answer_callback_query(call.id)

        corrida_service = services["corrida"]
        log = services["log"]

        chat_id = call.message.chat.id
        dados = registro_temp.get(chat_id)

        if not dados:
            log.warning("Sessão expirada ao confirmar")
            bot.send_message(chat_id, "❌ Sessão expirada.")
            return

        try:
            corrida_service.registrar_corrida(
                telegram_id=chat_id,
                tempo_segundos=dados["tempo_segundos"],
                distancia_metros=dados["distancia_metros"],
                passos=dados["passos"],
                calorias=dados["calorias"],
                tipo_treino=dados["tipo_treino"],
                local_treino=dados["local_treino"],
            )

            log.info(
                "Corrida registrada com sucesso",
                extra={
                    "telegram_id": chat_id,
                    "tempo_segundos": dados["tempo_segundos"],
                    "distancia_metros": dados["distancia_metros"],
                },
            )

            bot.send_message(chat_id, "✅ Corrida registrada com sucesso!")

        except Exception:
            log.exception("Erro ao registrar corrida")
            bot.send_message(chat_id, "❌ Erro ao registrar corrida.")

        finally:
            limpar_sessao(chat_id)

    # CALLBACK CANCELAR
    @bot.callback_query_handler(func=lambda call: call.data == "cancelar_registro")
    def callback_cancelar(call):

        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id
        limpar_sessao(chat_id)

        bot.send_message(chat_id, "❌ Registro cancelado.")


# ==========================================================
# TEMPO
# ==========================================================

def registrar_tempo(bot, services, message, correlation_id):

    log = services["log"]

    texto = message.text.strip()

    if usuario_cancelou(texto):
        limpar_sessao(message.chat.id)
        bot.send_message(message.chat.id, "❌ Registro cancelado.")
        return

    try:
        tempo_segundos = parse_tempo(texto)

        log.info(
            "Tempo informado",
            extra={
                "telegram_id": message.chat.id,
                "tempo_segundos": tempo_segundos,
            },
        )

        msg = bot.send_message(
            message.chat.id,
            "🏃 Distância (KM,metros)\nEx: 5,250"
        )

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


# ==========================================================
# DISTÂNCIA
# ==========================================================

def registrar_distancia(bot, services, message, tempo_segundos, correlation_id):

    log = services["log"]

    texto = message.text.strip()

    if usuario_cancelou(texto):
        limpar_sessao(message.chat.id)
        bot.send_message(message.chat.id, "❌ Registro cancelado.")
        return

    try:
        distancia_metros = parse_distancia(texto)

        log.info(
            "Distância informada",
            extra={
                "telegram_id": message.chat.id,
                "distancia_metros": distancia_metros,
            },
        )

        msg = bot.send_message(
            message.chat.id,
            "👟 Informe os passos (ou 0 se não souber)"
        )

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


# ==========================================================
# PASSOS
# ==========================================================

def registrar_passos(bot, services, message, tempo_segundos, distancia_metros, correlation_id):

    log = services["log"]

    texto = message.text.strip()

    if usuario_cancelou(texto):
        limpar_sessao(message.chat.id)
        bot.send_message(message.chat.id, "❌ Registro cancelado.")
        return

    try:
        passos = int(texto)

        log.info(
            "Passos informados",
            extra={
                "telegram_id": message.chat.id,
                "passos": passos,
            },
        )

        msg = bot.send_message(
            message.chat.id,
            "🔥 Informe as calorias (ou 0 se não souber)"
        )

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


# ==========================================================
# CALORIAS
# ==========================================================

def registrar_calorias(bot, services, message, tempo_segundos, distancia_metros, passos, correlation_id):

    log = services["log"]

    texto = message.text.strip()

    if usuario_cancelou(texto):
        limpar_sessao(message.chat.id)
        bot.send_message(message.chat.id, "❌ Registro cancelado.")
        return

    try:
        calorias = int(texto)

        log.info(
            "Calorias informadas",
            extra={
                "telegram_id": message.chat.id,
                "calorias": calorias,
            },
        )

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
