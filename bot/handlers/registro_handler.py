from datetime import datetime
from bot.state.registro_state import registro_temp, limpar_sessao
from bot.keyboards.menu_keyboard import menu_principal
from bot.keyboards.registro_keyboard import (
    teclado_tipo,
    teclado_local,
    teclado_confirmacao, 
    teclado_decisao_manual
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

    corrida_service = services["corrida"]
    log = services["log"]
    vision_service = services.get("vision")

    # ------------------------------------------------------
    # COMANDO /registrar
    # ------------------------------------------------------
    @bot.message_handler(commands=["registrar"])
    def registrar(message):
        registrar_command(bot, services, message)

    # ------------------------------------------------------
    # FOTO DO TREINO
    # ------------------------------------------------------
    @bot.message_handler(content_types=["photo"])
    def registrar_foto(message):

        if not vision_service:
            return

        chat_id = message.chat.id
        correlation_id = message.message_id

        log.info(
            "Foto recebida para análise",
            extra={
                "telegram_id": chat_id,
                "correlation_id": correlation_id,
            },
        )

        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            caminho = f"temp_{chat_id}.jpg"

            with open(caminho, "wb") as f:
                f.write(downloaded_file)

            resultado = vision_service.analisar_imagem(caminho)

            # --------------------------------------------------
            # ERRO NA IA
            # --------------------------------------------------
            if resultado.get("erro"):
                bot.send_message(chat_id, "❌ Erro ao processar imagem.")
                return

            # --------------------------------------------------
            # NÃO É TREINO → IGNORA AQUI
            # --------------------------------------------------
            if not resultado.get("eh_treino"):
                bot.send_message(
                    chat_id,
                    "⚠️ Não consegui identificar um treino nessa imagem.\n\n"
                    "Se quiser tentar novamente, envie outra imagem."
                )
                
                log.info(
                    "Imagem não é treino",
                    extra={"telegram_id": chat_id}
                )
                return  # deixa outros handlers tratarem

            # --------------------------------------------------
            # É TREINO → INICIA FLUXO
            # --------------------------------------------------
            if not resultado.get("tempo") or not resultado.get("distancia_km"):

                bot.send_message(
                    chat_id,
                    "⚠️ Não consegui identificar tempo ou distância.\n\n"
                    "Deseja registrar manualmente?",
                    reply_markup=teclado_decisao_manual()
                )
                return

            h, m, s = map(int, resultado["tempo"].split(":"))
            tempo_segundos = h * 3600 + m * 60 + s
            distancia_metros = float(resultado["distancia_km"]) * 1000

            log.info(
                "Treino identificado via imagem",
                extra={
                    "telegram_id": chat_id,
                    "tempo_segundos": tempo_segundos,
                    "distancia_metros": distancia_metros,
                },
            )

            registro_temp[chat_id] = {
                "tempo_segundos": tempo_segundos,
                "distancia_metros": distancia_metros,
                "passos": None,
                "calorias": None,
                "correlation_id": correlation_id,
            }

            msg = bot.send_message(
                chat_id,
                f"""
            🏃 Identifiquei um treino!

            📏 {resultado['distancia_km']} km
            ⏱ {resultado['tempo']}
            ⚡ Pace: {resultado.get('pace')}
            📅 {resultado.get('data')}

            Digite 'sair' para cancelar a qualquer momento.

            👟 Informe os passos (ou 0 se não souber)
            """
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
            log.exception("Erro ao analisar foto")
            bot.send_message(chat_id, "❌ Erro ao processar imagem.")
            limpar_sessao(chat_id)

    # ------------------------------------------------------
    # CALLBACK NÃO RECOCHECEU DADOS DA FOTO
    # ------------------------------------------------------
    @bot.callback_query_handler(func=lambda call: call.data in ["registro_manual_sim", "registro_manual_nao"])
    def callback_registro_manual(call):

        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id

        if call.data == "registro_manual_sim":
            registrar_command(bot, services, call.message)

        else:
            bot.send_message(
                chat_id,
                "Foi mal, vou tentar melhorar nos próximos updates.\n\n"
                "Se quiser tentar novamente, envie outra imagem."
            )

            bot.send_message(
                chat_id,
                "\nSe preferir, pode me perguntar o que quiser sobre o mundo da corrida ou dar uma olhada nas outras funções que fiz pra vc",
                reply_markup=menu_principal(),
                parse_mode="Markdown",
            )

    # ------------------------------------------------------
    # CALLBACK TIPO
    # ------------------------------------------------------
    @bot.callback_query_handler(func=lambda call: call.data.startswith("tipo_"))
    def callback_tipo(call):

        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id

        if chat_id not in registro_temp:
            bot.send_message(chat_id, "❌ Sessão expirada.")
            return

        tipo = call.data.replace("tipo_", "")
        registro_temp[chat_id]["tipo_treino"] = tipo

        bot.send_message(
            chat_id,
            "📍 Onde foi realizado o treino?",
            reply_markup=teclado_local()
        )

    # ------------------------------------------------------
    # CALLBACK LOCAL
    # ------------------------------------------------------
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

        bot.send_message(
            chat_id,
            "📅 Deseja informar a data e hora do treino?\n\n"
            "Formato: DD/MM/AAAA HH:MM\n"
            "Exemplo: 10/03/2025 06:30\n\n"
            "Digite 'pular' para usar a data atual.\n"
            "Digite 'sair' para cancelar."
        )

        bot.register_next_step_handler(
            call.message,
            lambda m: registrar_data_hora(bot, services, m)
        )


    # ------------------------------------------------------
    # DATA E HORA
    # ------------------------------------------------------
    def registrar_data_hora(bot, services, message):

        chat_id = message.chat.id
        texto = message.text.strip()

        if usuario_cancelou(texto):
            limpar_sessao(chat_id)
            bot.send_message(chat_id, "❌ Registro cancelado.")
            log.info(
                "Registro cancelado via texto",
                extra={"telegram_id": chat_id}
            )
            return

        if texto.lower() == "pular":
            registro_temp[chat_id]["data_corrida"] = None
        else:
            try:
                data_convertida = datetime.strptime(texto, "%d/%m/%Y %H:%M")
                registro_temp[chat_id]["data_corrida"] = data_convertida
            except ValueError:
                bot.send_message(
                    chat_id,
                    "❌ Formato inválido.\n\nUse: DD/MM/AAAA HH:MM\nOu digite 'pular'."
                )
                bot.register_next_step_handler(
                    message,
                    lambda m: registrar_data_hora(bot, services, m)
                )
                return

        mostrar_resumo_final(bot, services, message)


    # ------------------------------------------------------
    # RESUMO FINAL (COM PACE E DATA)
    # ------------------------------------------------------
    def mostrar_resumo_final(bot, services, message):

        chat_id = message.chat.id
        dados = registro_temp.get(chat_id)

        tempo_formatado = formatar_tempo(dados["tempo_segundos"])
        distancia_formatada = formatar_distancia(dados["distancia_metros"])

        pace_segundos = dados.get("pace_segundos")

        # Se não foi informado manualmente, calcula para exibir no resumo
        if pace_segundos is None:
            corrida_service = services["corrida"]
            pace_segundos = corrida_service.calcular_pace(
                dados["tempo_segundos"],
                dados["distancia_metros"]
            )

        pace_min = pace_segundos // 60
        pace_sec = pace_segundos % 60
        pace_formatado = f"{pace_min:02d}:{pace_sec:02d}"
        # else:
        #     pace_formatado = "N/A"

        data_info = (
            dados["data_corrida"].strftime("%d/%m/%Y %H:%M")
            if dados.get("data_corrida")
            else "Data atual"
        )

        resumo = (
            "📋 *Resumo do treino*\n\n"
            f"⏱ Tempo: {tempo_formatado}\n"
            f"📏 Distância: {distancia_formatada}\n"
            f"⚡ Pace: {pace_formatado}\n"
            f"👟 Passos: {dados['passos']}\n"
            f"🔥 Calorias: {dados['calorias']}\n"
            f"🏷 Tipo: {dados['tipo_treino']}\n"
            f"📍 Local: {dados['local_treino']}\n"
            f"📅 Data: {data_info}\n\n"
            "Confirmar registro?"
        )

        bot.send_message(
            chat_id,
            resumo,
            reply_markup=teclado_confirmacao(),
            parse_mode="Markdown"
        )

    # ------------------------------------------------------
    # CALLBACK CONFIRMAR
    # ------------------------------------------------------
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
                pace_segundos=dados.get("pace_segundos"),
                # pace_origem=dados.get("pace_origem"),
                data_corrida=dados.get("data_corrida")
            )

            bot.send_message(chat_id, "✅ Corrida registrada com sucesso!")
            log.info(
                "CORRIDA REGISTRADA",
                extra={
                    "telegram_id": chat_id,
                    "correlation_id": dados["correlation_id"],
                },
            )

        except Exception:
            log.exception("Erro ao registrar corrida")
            bot.send_message(chat_id, "❌ Erro ao registrar corrida.")

        finally:
            limpar_sessao(chat_id)

    # ------------------------------------------------------
    # CALLBACK CANCELAR
    # ------------------------------------------------------
    @bot.callback_query_handler(func=lambda call: call.data == "cancelar_registro")
    def callback_cancelar(call):

        bot.answer_callback_query(call.id)
        limpar_sessao(call.message.chat.id)
        bot.send_message(call.message.chat.id, "❌ Registro cancelado.")
        log.info(
            "Registro cancelado via botão",
            extra={"telegram_id": call.message.chat.id}
        )


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
