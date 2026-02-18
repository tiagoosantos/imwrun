from ia.gemini import responder_com_ia


def register_ia(bot, services):

    log = services["log"]

    # =======================
    # FALLBACK IA
    # =======================

    @bot.message_handler(
        func=lambda m: (m.text and not m.text.startswith("/"))
    )
    def fallback_ia(message):

        try:

            log.info(
                "Fallback IA acionado",
                extra={
                    "telegram_id": message.chat.id,
                    "texto": message.text,
                },
            )

            responder_com_ia(bot, message)

        except Exception:

            log.exception(
                "Erro no fallback IA",
                extra={
                    "telegram_id": message.chat.id,
                },
            )

            bot.send_message(
                message.chat.id,
                "❌ Ocorreu um erro ao processar sua mensagem."
            )
