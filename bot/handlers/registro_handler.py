from bot.state.registro_state import registro_temp, limpar_sessao
from bot.keyboards.registro_keyboard import (teclado_tipo, teclado_local, teclado_confirmacao)
from bot.utils.bot_utils import (usuario_cancelou, parse_tempo, parse_distancia, formatar_tempo, formatar_distancia)

def register_registro(bot, services):

    corrida_service = services["corrida"]
    log = services["log"]

    # =======================
    # /registrar
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

        msg = bot.send_message(
            message.chat.id,
            "⏱ Informe o tempo (MM:SS)\n\nDigite 'sair' para cancelar."
        )

        bot.register_next_step_handler(msg, registrar_tempo, correlation_id)

    # =======================
    # TEMPO
    # =======================

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

            msg = bot.send_message(
                message.chat.id,
                "🏃 Distância no formato KM,metros\nEx: 5,250\n\nDigite 'sair' para cancelar."
            )

            bot.register_next_step_handler(
                msg,
                registrar_distancia,
                tempo_segundos,
                correlation_id
            )

        except Exception:

            log.warning(
                "Tempo inválido",
                extra={
                    "telegram_id": message.chat.id,
                    "correlation_id": correlation_id,
                    "valor": message.text,
                },
            )

            bot.send_message(
                message.chat.id,
                "❌ Formato inválido. Use MM:SS\n\nDigite 'sair' para cancelar."
            )

            bot.register_next_step_handler(
                message,
                registrar_tempo,
                correlation_id
            )

    # =======================
    # DISTÂNCIA
    # =======================

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
            distancia_metros = parse_distancia(texto)

            log.info(
                "Distância informada",
                extra={
                    "telegram_id": message.chat.id,
                    "correlation_id": correlation_id,
                    "distancia_metros": distancia_metros,
                },
            )

            msg = bot.send_message(
                message.chat.id,
                "👟 Informe os passos (ou 0 se não souber)\n\nDigite 'sair' para cancelar."
            )

            bot.register_next_step_handler(
                msg,
                registrar_passos,
                tempo_segundos,
                distancia_metros,
                correlation_id
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

            bot.send_message(
                message.chat.id,
                "❌ Distância inválida. Use KM,metros (Ex: 5,250)\n\nOu digite 'sair' para cancelar."
            )

            bot.register_next_step_handler(
                message,
                registrar_distancia,
                tempo_segundos,
                correlation_id
            )

    # =======================
    # PASSOS
    # =======================

    def registrar_passos(message, tempo_segundos, distancia_metros, correlation_id):

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

            msg = bot.send_message(
                message.chat.id,
                "🔥 Informe as calorias (ou 0 se não souber)\n\nDigite 'sair' para cancelar."
            )

            bot.register_next_step_handler(
                msg,
                registrar_calorias,
                tempo_segundos,
                distancia_metros,
                passos,
                correlation_id
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

            bot.send_message(
                message.chat.id,
                "❌ Informe apenas número inteiro.\n\nDigite 'sair' para cancelar."
            )

            bot.register_next_step_handler(
                message,
                registrar_passos,
                tempo_segundos,
                distancia_metros,
                correlation_id
            )

    # =======================
    # CALORIAS
    # =======================

    def registrar_calorias(message, tempo_segundos, distancia_metros, passos, correlation_id):

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

            log.warning(
                "Calorias inválidas",
                extra={
                    "telegram_id": message.chat.id,
                    "correlation_id": correlation_id,
                    "valor": message.text,
                },
            )

            bot.send_message(
                message.chat.id,
                "❌ Informe apenas número inteiro.\n\nDigite 'sair' para cancelar."
            )

            bot.register_next_step_handler(
                message,
                registrar_calorias,
                tempo_segundos,
                distancia_metros,
                passos,
                correlation_id
            )

    # =======================
    # CALLBACK TIPO
    # =======================

    @bot.callback_query_handler(func=lambda call: call.data.startswith("tipo_"))
    def callback_tipo(call):

        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id

        if chat_id not in registro_temp:
            bot.send_message(chat_id, "❌ Sessão expirada.")
            return

        tipo = call.data.replace("tipo_", "")

        registro_temp[chat_id].update({"tipo_treino": tipo})

        bot.send_message(
            chat_id,
            "📍 Onde foi realizado o treino?",
            reply_markup=teclado_local()
        )

    # =======================
    # CALLBACK LOCAL
    # =======================

    @bot.callback_query_handler(func=lambda call: call.data.startswith("local_"))
    def callback_local(call):

        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id
        dados = registro_temp.get(chat_id)

        if not dados:
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

    # =======================
    # CONFIRMAR
    # =======================

    @bot.callback_query_handler(func=lambda call: call.data == "confirmar_registro")
    def callback_confirmar(call):

        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id
        dados = registro_temp.get(chat_id)

        if not dados:
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
                "Corrida confirmada pelo usuário",
                extra={
                    "telegram_id": chat_id,
                    "correlation_id": dados["correlation_id"],
                },
            )

            bot.send_message(chat_id, "✅ Corrida registrada com sucesso!")

        except Exception:

            log.exception(
                "Erro ao registrar corrida",
                extra={
                    "telegram_id": chat_id,
                    "correlation_id": dados["correlation_id"],
                },
            )

            bot.send_message(chat_id, "❌ Erro ao registrar corrida.")

        finally:
            limpar_sessao(chat_id)

    # =======================
    # CANCELAR
    # =======================

    @bot.callback_query_handler(func=lambda call: call.data == "cancelar_registro")
    def callback_cancelar(call):

        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id

        limpar_sessao(chat_id)

        bot.send_message(chat_id, "❌ Registro cancelado.")
