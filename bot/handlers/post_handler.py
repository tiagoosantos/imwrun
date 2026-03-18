import threading
from concurrent.futures import ThreadPoolExecutor

from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    InputMediaPhoto,
)

from bot.state.post_state import post_temp, post_timers
from bot.utils.bot_utils import formatar_distancia, formatar_tempo
from service.post_service import GEMINI_ATIVO


executor = ThreadPoolExecutor(max_workers=3)


POST_ESCOLHENDO_TREINO = "post_escolhendo_treino"
POST_AGUARDANDO_FOTO = "post_aguardando_foto"
POST_ESCOLHENDO_ESTILO = "post_escolhendo_estilo"


def criar_markup_estilo():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Premium", callback_data="post_estilo_premium"),
        InlineKeyboardButton("Clean", callback_data="post_estilo_clean"),
        InlineKeyboardButton("Artistico", callback_data="post_estilo_artistico"),
        InlineKeyboardButton("Cartoon", callback_data="post_estilo_cartoon"),
    )
    return markup


def iniciar_post_command(bot, services, message):
    post_service = services["post"]
    corrida_service = services["corrida"]
    log = services["log"]

    telegram_id = message.chat.id
    correlation_id = message.message_id

    log.info(
        "Iniciando fluxo de postar treino",
        extra={
            "telegram_id": telegram_id,
            "correlation_id": correlation_id,
        },
    )

    if not post_service.pode_gerar_post(telegram_id):
        log.info(
            "Limite diario de post atingido",
            extra={
                "telegram_id": telegram_id,
                "correlation_id": correlation_id,
            },
        )

        bot.send_message(
            telegram_id,
            "Voce ja utilizou suas 2 geracoes hoje.\nTente novamente amanha.",
        )
        return

    treinos = corrida_service.listar_ultimos(telegram_id)

    if not treinos:
        log.info(
            "Usuario tentou postar sem treinos",
            extra={
                "telegram_id": telegram_id,
                "correlation_id": correlation_id,
            },
        )

        bot.send_message(
            telegram_id,
            "Voce ainda nao possui treinos registrados.",
        )
        return

    post_temp[telegram_id] = {
        "estado": POST_ESCOLHENDO_TREINO,
        "treino_id": None,
        "foto": None,
        "prompt_tipo": None,
        "correlation_id": correlation_id,
    }

    markup = InlineKeyboardMarkup()

    for treino in treinos:
        treino_id = treino[0]
        distancia = formatar_distancia(treino[1])
        tempo = formatar_tempo(treino[2])

        markup.add(
            InlineKeyboardButton(
                f"{distancia} - {tempo}",
                callback_data=f"post_treino_{treino_id}",
            )
        )

    bot.send_message(
        telegram_id,
        "Escolha o treino para gerar o post:",
        reply_markup=markup,
    )


def register_post(bot, services):
    post_service = services["post"]
    log = services["log"]

    @bot.callback_query_handler(func=lambda c: c.data == "cmd_postar")
    def iniciar_post_callback(call):
        bot.answer_callback_query(call.id)
        iniciar_post_command(bot, services, call.message)

    @bot.callback_query_handler(func=lambda c: c.data.startswith("post_treino_"))
    def escolher_treino(call):
        telegram_id = call.message.chat.id
        data = post_temp.get(telegram_id)

        if not data or data.get("estado") != POST_ESCOLHENDO_TREINO:
            return

        treino_id = int(call.data.split("_")[-1])
        correlation_id = data["correlation_id"]

        log.info(
            "Treino selecionado para gerar post",
            extra={
                "telegram_id": telegram_id,
                "correlation_id": correlation_id,
                "treino_id": treino_id,
            },
        )

        data["treino_id"] = treino_id
        data["estado"] = POST_AGUARDANDO_FOTO

        bot.answer_callback_query(call.id)
        bot.send_message(
            telegram_id,
            "Agora envie uma foto para gerar o post.",
        )

    @bot.callback_query_handler(func=lambda c: c.data.startswith("post_estilo_"))
    def escolher_estilo(call):
        telegram_id = call.message.chat.id
        data = post_temp.get(telegram_id)

        if not data or data.get("estado") != POST_ESCOLHENDO_ESTILO:
            return

        correlation_id = data["correlation_id"]
        prompt_tipo = call.data.replace("post_estilo_", "")
        data["prompt_tipo"] = prompt_tipo
        data["gerando"] = True

        log.info(
            "Estilo selecionado para gerar imagem IA",
            extra={
                "telegram_id": telegram_id,
                "correlation_id": correlation_id,
                "prompt_tipo": prompt_tipo,
            },
        )

        bot.answer_callback_query(call.id)
        bot.send_message(telegram_id, "Gerando seu post...")
        bot.send_chat_action(telegram_id, "upload_photo")

        executor.submit(
            gerar_post_final,
            bot,
            telegram_id,
            services,
        )

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: post_temp.get(m.chat.id, {}).get("estado") == POST_AGUARDANDO_FOTO,
    )
    def receber_foto(message):
        telegram_id = message.chat.id
        data = post_temp.get(telegram_id)

        if not data:
            return

        if data.get("gerando"):
            bot.send_message(
                telegram_id,
                "Ja estou gerando um post para voce, aguarde.",
            )
            return

        correlation_id = data["correlation_id"]

        try:
            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            path = post_service.salvar_foto_temporaria(downloaded_file)

            data["foto"] = path

            log.info(
                "Foto recebida para gerar post",
                extra={
                    "telegram_id": telegram_id,
                    "correlation_id": correlation_id,
                },
            )

            if GEMINI_ATIVO:
                data["estado"] = POST_ESCOLHENDO_ESTILO
                data["prompt_tipo"] = "artistico"

                bot.send_message(
                    telegram_id,
                    "Escolha o estilo da imagem gerada por IA:",
                    reply_markup=criar_markup_estilo(),
                )
                return

            data["gerando"] = True
            bot.send_message(telegram_id, "Gerando seu post...")
            bot.send_chat_action(telegram_id, "upload_photo")

            executor.submit(
                gerar_post_final,
                bot,
                telegram_id,
                services,
            )

        except Exception as e:
            log.error(
                f"Erro ao processar foto: {e}",
                extra={
                    "telegram_id": telegram_id,
                    "correlation_id": correlation_id,
                },
            )

            bot.send_message(
                telegram_id,
                "Erro ao processar a foto.",
            )

            post_temp.pop(telegram_id, None)

    @bot.message_handler(commands=["cancelar"])
    def cancelar_post(message):
        telegram_id = message.chat.id
        data = post_temp.get(telegram_id)

        if not data:
            bot.send_message(
                telegram_id,
                "Nenhum post em andamento para cancelar.",
            )
            return

        timer = post_timers.pop(telegram_id, None)
        if timer:
            timer.cancel()

        post_temp.pop(telegram_id, None)

        bot.send_message(
            telegram_id,
            "Geracao de post cancelada com sucesso.",
        )


def gerar_post_final(bot, telegram_id, services):
    post_service = services["post"]
    log = services["log"]

    data = post_temp.get(telegram_id)

    if not data:
        return

    correlation_id = data["correlation_id"]

    try:
        bot.send_message(telegram_id, "Ta pronto o seu post...")

        resultado = post_service.gerar_post(
            telegram_id=telegram_id,
            treino_id=data["treino_id"],
            fotos=[data["foto"]],
            prompt_tipo=data.get("prompt_tipo") or "artistico",
        )

        if isinstance(resultado, dict) and resultado.get("aguardar"):
            segundos = resultado["segundos"]

            bot.send_message(
                telegram_id,
                f"Muitas solicitacoes no momento.\n"
                f"Aguardando {segundos} segundos para tentar novamente...",
            )

            timer_existente = post_timers.get(telegram_id)
            if timer_existente:
                timer_existente.cancel()

            timer = threading.Timer(
                segundos,
                gerar_post_final,
                args=(bot, telegram_id, services),
            )

            post_timers[telegram_id] = timer
            timer.start()
            return

        imagens = resultado

        log.info(
            "Post gerado com sucesso",
            extra={
                "telegram_id": telegram_id,
                "correlation_id": correlation_id,
            },
        )

        media = []

        for img in imagens:
            file = open(img, "rb")
            media.append(InputMediaPhoto(file))

        bot.send_media_group(telegram_id, media)

        for m in media:
            m.media.close()

        post_temp.pop(telegram_id, None)

        timer = post_timers.pop(telegram_id, None)
        if timer:
            timer.cancel()

    except Exception as e:
        log.error(
            f"Erro ao gerar post: {e}",
            extra={
                "telegram_id": telegram_id,
                "correlation_id": correlation_id,
            },
        )

        bot.send_message(
            telegram_id,
            "Ocorreu um erro ao gerar o post.",
        )

        post_temp.pop(telegram_id, None)

        timer = post_timers.pop(telegram_id, None)
        if timer:
            timer.cancel()
