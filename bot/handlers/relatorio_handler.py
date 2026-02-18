def register_relatorio(bot, services):

    relatorio_service = services["relatorio"]
    log = services["log"]

    # =======================
    # /relatorio
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

        bot.register_next_step_handler(
            msg,
            gerar_relatorio,
            correlation_id
        )

    # =======================
    # GERAR RELATÓRIO
    # =======================

    def gerar_relatorio(message, correlation_id):

        if not message.text:
            return

        try:

            mes = message.text.strip()

            arquivo = relatorio_service.gerar_relatorio_mensal(mes)

            log.info(
                "Relatório gerado",
                extra={
                    "telegram_id": message.chat.id,
                    "correlation_id": correlation_id,
                    "mes": mes,
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

            bot.send_message(
                message.chat.id,
                "❌ Erro ao gerar relatório."
            )
