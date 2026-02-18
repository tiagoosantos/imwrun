from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def register_ranking(bot, services):

    corrida_service = services["corrida"]
    log = services["log"]

    # =======================
    # /ranking_km
    # =======================

    @bot.message_handler(commands=["ranking_km"])
    def ranking_km(message):

        correlation_id = message.message_id
        pagina = 1

        enviar_ranking_km(
            chat_id=message.chat.id,
            pagina=pagina,
            correlation_id=correlation_id
        )

    # =======================
    # CALLBACK PAGINAÇÃO KM
    # =======================

    @bot.callback_query_handler(func=lambda call: call.data.startswith("ranking_km_"))
    def callback_ranking_km(call):

        bot.answer_callback_query(call.id)

        correlation_id = call.message.message_id
        chat_id = call.message.chat.id

        pagina = int(call.data.split("_")[-1])

        enviar_ranking_km(
            chat_id=chat_id,
            pagina=pagina,
            correlation_id=correlation_id
        )

    # =======================
    # ENVIO RANKING KM
    # =======================

    def enviar_ranking_km(chat_id, pagina, correlation_id):

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

        # Busca 1 registro extra para saber se há próxima página
        ranking = corrida_service.obter_ranking_km(
            limit=limit + 1,
            offset=offset
        )

        tem_proxima = len(ranking) > limit
        ranking = ranking[:limit]

        if not ranking:
            bot.send_message(chat_id, "📭 Página vazia.")
            return

        texto = f"🏆 *Ranking por KM – Página {pagina}*\n\n"

        for pos, (_, nome, total_km) in enumerate(ranking, start=offset + 1):
            texto += f"{pos}º - {nome}: {float(total_km):.2f} km\n"

        # ======================
        # BOTÕES PAGINAÇÃO
        # ======================

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

    # =======================
    # /ranking_tempo
    # =======================

    @bot.message_handler(commands=["ranking_tempo"])
    def ranking_tempo(message):

        correlation_id = message.message_id

        log.info(
            "Ranking tempo solicitado",
            extra={
                "telegram_id": message.chat.id,
                "correlation_id": correlation_id,
            },
        )

        ranking = corrida_service.obter_ranking_tempo(limit=10)

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
