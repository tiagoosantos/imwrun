# ==========================================================
# FUNÇÃO PRINCIPAL REUTILIZÁVEL
# ==========================================================

def relatorio_command(bot, services, message):

    relatorio_service = services["relatorio"]
    log = services["log"]

    # limpa qualquer step pendente
    bot.clear_step_handler_by_chat_id(message.chat.id)

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
        "📅 Informe o mês no formato YYYY-MM\n"
        "Ex: 2026-01\n\n"
        "Digite 'sair' para cancelar."
    )

    bot.register_next_step_handler(
        msg,
        lambda m: gerar_relatorio(
            bot,
            services,
            m,
            correlation_id
        )
    )


# ==========================================================
# REGISTRO DO COMMAND HANDLER
# ==========================================================

def register_relatorio(bot, services):

    @bot.message_handler(commands=["relatorio"])
    def relatorio(message):
        relatorio_command(bot, services, message)


# ==========================================================
# GERAR RELATÓRIO
# ==========================================================

def gerar_relatorio(bot, services, message, correlation_id):

    relatorio_service = services["relatorio"]
    log = services["log"]

    if not message.text:
        return

    texto = message.text.strip()

    if texto.lower() == "sair":
        bot.send_message(message.chat.id, "❌ Operação cancelada.")
        return

    try:

        mes = texto

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
            "❌ Erro ao gerar relatório.\n"
            "Verifique o formato YYYY-MM.\n\n"
            "Digite 'sair' para cancelar."
        )

        # permite tentar novamente
        bot.register_next_step_handler(
            message,
            lambda m: gerar_relatorio(
                bot,
                services,
                m,
                correlation_id
            )
        )
