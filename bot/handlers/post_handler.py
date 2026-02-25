from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto
)

from bot.state.post_state import post_temp
from bot.utils.bot_utils import formatar_tempo, formatar_distancia


# ==========================
# ESTADOS
# ==========================

POST_ESCOLHENDO_TREINO = "post_escolhendo_treino"
POST_AGUARDANDO_FOTO = "post_aguardando_foto"


# ==========================================================
# INÍCIO DO FLUXO
# ==========================================================

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
            "correlation_id": correlation_id
        }
    )

    if not post_service.pode_gerar_post(telegram_id):

        log.info(
            "Limite diário de post atingido",
            extra={
                "telegram_id": telegram_id,
                "correlation_id": correlation_id
            }
        )

        bot.send_message(
            telegram_id,
            "⚠️ Você já utilizou suas 2 gerações hoje.\nTente novamente amanhã."
        )
        return

    treinos = corrida_service.listar_ultimos(telegram_id)

    if not treinos:

        log.info(
            "Usuário tentou postar sem treinos",
            extra={
                "telegram_id": telegram_id,
                "correlation_id": correlation_id
            }
        )

        bot.send_message(
            telegram_id,
            "Você ainda não possui treinos registrados."
        )
        return

    post_temp[telegram_id] = {
        "estado": POST_ESCOLHENDO_TREINO,
        "treino_id": None,
        "foto": None,
        "correlation_id": correlation_id
    }

    markup = InlineKeyboardMarkup()

    for treino in treinos:
        treino_id = treino[0]
        distancia = formatar_distancia(treino[1])
        tempo = formatar_tempo(treino[2])

        markup.add(
            InlineKeyboardButton(
                f"{distancia} - {tempo}",
                callback_data=f"post_treino_{treino_id}"
            )
        )

    bot.send_message(
        telegram_id,
        "🏃 Escolha o treino para gerar o post:",
        reply_markup=markup
    )


# ==========================================================
# REGISTRO DOS HANDLERS
# ==========================================================

def register_post(bot, services):

    post_service = services["post"]
    log = services["log"]

    # ------------------------------------------------------
    # Callback do menu
    # ------------------------------------------------------

    @bot.callback_query_handler(func=lambda c: c.data == "cmd_postar")
    def iniciar_post_callback(call):

        bot.answer_callback_query(call.id)

        iniciar_post_command(bot, services, call.message)

    # ------------------------------------------------------
    # Escolher treino
    # ------------------------------------------------------

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
                "treino_id": treino_id
            }
        )

        data["treino_id"] = treino_id
        data["estado"] = POST_AGUARDANDO_FOTO

        bot.edit_message_text(
            "📸 Agora envie uma foto para gerar o post.",
            telegram_id,
            call.message.message_id
        )

    # ------------------------------------------------------
    # Receber foto
    # ------------------------------------------------------

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: post_temp.get(m.chat.id, {}).get("estado") == POST_AGUARDANDO_FOTO
    )
    def receber_foto(message):

        telegram_id = message.chat.id
        data = post_temp.get(telegram_id)

        if not data:
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
                    "correlation_id": correlation_id
                }
            )

            gerar_post_final(bot, telegram_id, services)

        except Exception as e:

            log.error(
                f"Erro ao processar foto: {e}",
                extra={
                    "telegram_id": telegram_id,
                    "correlation_id": correlation_id
                }
            )

            bot.send_message(
                telegram_id,
                "❌ Erro ao processar a foto."
            )

            post_temp.pop(telegram_id, None)


# ==========================================================
# GERAÇÃO FINAL
# ==========================================================

def gerar_post_final(bot, telegram_id, services):

    post_service = services["post"]
    log = services["log"]

    data = post_temp.get(telegram_id)

    if not data:
        return

    correlation_id = data["correlation_id"]

    bot.send_message(telegram_id, "⏳ Gerando seu post...")

    try:

        imagens = post_service.gerar_post(
            telegram_id=telegram_id,
            treino_id=data["treino_id"],
            fotos=[data["foto"]]
        )

        log.info(
            "Post gerado com sucesso",
            extra={
                "telegram_id": telegram_id,
                "correlation_id": correlation_id
            }
        )

        media = []

        for img in imagens:
            file = open(img, "rb")
            media.append(InputMediaPhoto(file))

        bot.send_media_group(telegram_id, media)

        for m in media:
            m.media.close()

        post_service.limpar_arquivos(imagens)

    except Exception as e:

        log.error(
            f"Erro ao gerar post: {e}",
            extra={
                "telegram_id": telegram_id,
                "correlation_id": correlation_id
            }
        )

        bot.send_message(
            telegram_id,
            "❌ Ocorreu um erro ao gerar o post."
        )

    finally:
        post_temp.pop(telegram_id, None)