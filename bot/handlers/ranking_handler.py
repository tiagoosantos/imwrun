from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==================================================
# FUNÇÕES REUTILIZÁVEIS
# ==================================================

def ranking_km_command(bot, services, message):

    corrida_service = services["corrida"]
    log = services["log"]

    # limpa qualquer fluxo pendente
    bot.clear_step_handler_by_chat_id(message.chat.id)

    correlation_id = message.message_id
    pagina = 1

    enviar_ranking_km(
        bot,
        corrida_service,
        log,
        chat_id=message.chat.id,
        pagina=pagina,
        correlation_id=correlation_id
    )


def ranking_tempo_command(bot, services, message):

    corrida_service = services["corrida"]
    log = services["log"]

    bot.clear_step_handler_by_chat_id(message.chat.id)

    correlation_id = message.message_id

    log.info(
        "Ranking tempo solicitado",
        extra={
            "telegram_id": message.chat.id,
            "correlation_id": correlation_id,
        },
    )

    try:
        ranking = corrida_service.obter_ranking_tempo(limit=10)
    except Exception:
        log.exception("Erro ao buscar ranking tempo")
        bot.send_message(message.chat.id, "❌ Erro ao buscar ranking.")
        return

    if not ranking:
        bot.send_message(message.chat.id, "📭 Nenhuma corrida registrada.")
        return

    texto = "⏱ *Ranking por Tempo*\n\n"

    for pos, (_, nome, tempo_total) in enumerate(ranking, start=1):
        minutos = tempo_total // 60
        segundos = tempo_total % 60
        texto += f"{pos}º - {nome}: {minutos:02d}:{segundos:02d}\n"

    bot.send_message(
        message.chat.id,
        texto,
        parse_mode="Markdown"
    )


# ==================================================
# FUNÇÃO INTERNA DE ENVIO (PAGINAÇÃO KM)
# ==================================================

def enviar_ranking_km(bot, corrida_service, log, chat_id, pagina, correlation_id):

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

    try:
        ranking = corrida_service.obter_ranking_km(
            limit=limit + 1,
            offset=offset
        )
    except Exception:
        log.exception("Erro ao buscar ranking KM")
        bot.send_message(chat_id, "❌ Erro ao buscar ranking.")
        return

    tem_proxima = len(ranking) > limit
    ranking = ranking[:limit]

    if not ranking:
        bot.send_message(chat_id, "📭 Página vazia.")
        return

    texto = f"🏆 *Ranking por KM – Página {pagina}*\n\n"

    for pos, (_, nome, total_km) in enumerate(ranking, start=offset + 1):
        texto += f"{pos}º - {nome}: {float(total_km):.2f} km\n"

    markup = InlineKeyboardMarkup(row_width=2)
    botoes = []

    if pagina > 1:
        botoes.append(
            InlineKeyboardButton(
                "⬅ Anterior",
                callback_data=f"ranking_km_{pagina-1}"
            )
        )

    if tem_proxima:
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


# ==================================================
# REGISTRO DOS COMMAND HANDLERS
# ==================================================

def register_ranking(bot, services):

    @bot.message_handler(commands=["ranking_km"])
    def ranking_km(message):
        ranking_km_command(bot, services, message)

    @bot.message_handler(commands=["ranking_tempo"])
    def ranking_tempo(message):
        ranking_tempo_command(bot, services, message)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("ranking_km_"))
    def callback_ranking_km(call):

        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id
        correlation_id = call.message.message_id
        pagina = int(call.data.split("_")[-1])

        corrida_service = services["corrida"]
        log = services["log"]

        enviar_ranking_km(
            bot,
            corrida_service,
            log,
            chat_id=chat_id,
            pagina=pagina,
            correlation_id=correlation_id
        )
