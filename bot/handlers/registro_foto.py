import os
from bot.state.registro_state import registro_temp
from bot.keyboards.menu_keyboard import menu_principal
from bot.keyboards.registro_keyboard import teclado_decisao_manual
from .registro_manual import registrar_passos
from bot.utils.timeout_manager import iniciar_timeout, cancelar_timeout


def processar_foto(bot, services, message):

    vision_service = services.get("vision")
    log = services["log"]

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
        os.remove(caminho)

        if resultado.get("erro"):
            bot.send_message(chat_id, "❌ Erro ao processar imagem.")
            return

        if not resultado.get("eh_treino"):
            bot.send_message(
                chat_id,
                "⚠️ Eita, não consegui identificar um treino nessa imagem.\n"
                "Se quiser tentar de novo é só me mandar outra imagem.\n\n"
                "Mas se preferir, a gente pode registrar o treino manualmente. Se quiser é só clicar no SIM"
                "Se quiser tentar outra hora, sem problemas, é só clicar no NÃO",
                reply_markup=teclado_decisao_manual()
            )
            
            bot.send_message(
                chat_id,
                "\nJá vou deixar aqui o menu principal pra você dar uma olhada nas outras funções que fiz pra te ajudar no mundo da corrida",
                reply_markup=menu_principal(),
                parse_mode="Markdown",
            )

            log.info(
                "Imagem não é treino",
                extra={
                    "telegram_id": chat_id,
                    "correlation_id": correlation_id,
                },
            )
            return

        if not resultado.get("tempo") or not resultado.get("distancia_km"):
            bot.send_message(
                chat_id,
                "⚠️ Consegui identificar que é um treino, mas não consegui extrair tempo ou distância.\n\n"
                "Foi mal, vou tentar melhorar nos próximos updates.\n\n"
                "Se quiser tentar novamente, envie outra imagem.",
                # reply_markup=teclado_decisao_manual()
            )
            
            bot.send_message(
                chat_id,
                "\nSe preferir, pode me perguntar o que quiser sobre o mundo da corrida ou dar uma olhada nas outras funções que fiz pra vc",
                reply_markup=menu_principal(),
                parse_mode="Markdown",
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
                "correlation_id": correlation_id
            }
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
        iniciar_timeout(bot, chat_id)

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