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
POST_ESCOLHENDO_PROMPT = "post_escolhendo_prompt"
POST_AGUARDANDO_FOTOS = "post_aguardando_fotos"
POST_AGUARDANDO_PROMPT_CUSTOM = "post_aguardando_prompt_custom"


# ==========================================================
# INÍCIO DO FLUXO (chamado pelo menu)
# ==========================================================

def iniciar_post_command(bot, services, message):

    post_service = services["post"]
    corrida_service = services["corrida"]
    log = services["log"]

    telegram_id = message.chat.id

    if not post_service.pode_gerar_post(telegram_id):
        bot.send_message(
            telegram_id,
            "⚠️ Você já utilizou suas 2 gerações hoje.\nTente novamente amanhã."
        )
        return

    treinos = corrida_service.listar_ultimos(telegram_id)

    if not treinos:
        bot.send_message(
            telegram_id,
            "Você ainda não possui treinos registrados."
        )
        return

    post_temp[telegram_id] = {
        "estado": POST_ESCOLHENDO_TREINO,
        "treino_id": None,
        "prompt": None,
        "fotos": []
    }

    markup = InlineKeyboardMarkup()

    for treino in treinos:
        treino_id = treino[0]
        distancia_formatada = formatar_distancia(treino[1])
        tempo_formatado = formatar_tempo(treino[2])

        markup.add(
            InlineKeyboardButton(
                f"{distancia_formatada} - {tempo_formatado}",
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
    # Callback do menu principal
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

        if post_temp.get(telegram_id, {}).get("estado") != POST_ESCOLHENDO_TREINO:
            return

        treino_id = int(call.data.split("_")[-1])
        post_temp[telegram_id]["treino_id"] = treino_id
        post_temp[telegram_id]["estado"] = POST_ESCOLHENDO_PROMPT

        prompts = post_service.listar_prompts_modelo()

        markup = InlineKeyboardMarkup()

        for key, titulo in prompts.items():
            markup.add(
                InlineKeyboardButton(
                    titulo,
                    callback_data=f"post_prompt_{key}"
                )
            )

        markup.add(
            InlineKeyboardButton(
                "✍️ Criar meu próprio prompt",
                callback_data="post_prompt_custom"
            )
        )

        bot.edit_message_text(
            "🎨 Escolha o estilo do post:",
            telegram_id,
            call.message.message_id,
            reply_markup=markup
        )

    # ------------------------------------------------------
    # Escolher prompt
    # ------------------------------------------------------

    @bot.callback_query_handler(func=lambda c: c.data.startswith("post_prompt_"))
    def escolher_prompt(call):

        telegram_id = call.message.chat.id

        if post_temp.get(telegram_id, {}).get("estado") != POST_ESCOLHENDO_PROMPT:
            return

        if call.data == "post_prompt_custom":
            post_temp[telegram_id]["estado"] = POST_AGUARDANDO_PROMPT_CUSTOM
            bot.send_message(
                telegram_id,
                "✍️ Envie o prompt que deseja utilizar:"
            )
            return

        prompt_key = call.data.replace("post_prompt_", "")
        prompt = post_service.obter_prompt_modelo(prompt_key)

        post_temp[telegram_id]["prompt"] = prompt
        post_temp[telegram_id]["estado"] = POST_AGUARDANDO_FOTOS

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                "✅ Finalizar envio",
                callback_data="post_finalizar_fotos"
            )
        )

        bot.send_message(
            telegram_id,
            "📸 Agora envie uma ou mais fotos.\nQuando terminar, clique em Finalizar.",
            reply_markup=markup
        )

    # ------------------------------------------------------
    # Prompt custom
    # ------------------------------------------------------

    @bot.message_handler(
        func=lambda m: post_temp.get(m.chat.id, {}).get("estado") == POST_AGUARDANDO_PROMPT_CUSTOM
    )
    def receber_prompt_custom(message):

        telegram_id = message.chat.id

        post_temp[telegram_id]["prompt"] = message.text
        post_temp[telegram_id]["estado"] = POST_AGUARDANDO_FOTOS

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                "✅ Finalizar envio",
                callback_data="post_finalizar_fotos"
            )
        )

        bot.send_message(
            telegram_id,
            "📸 Agora envie uma ou mais fotos.\nQuando terminar, clique em Finalizar.",
            reply_markup=markup
        )

    # ------------------------------------------------------
    # Receber fotos
    # ------------------------------------------------------

    @bot.message_handler(
        content_types=["photo"],
        func=lambda m: post_temp.get(m.chat.id, {}).get("estado") == POST_AGUARDANDO_FOTOS
    )
    def receber_foto(message):

        try:
            telegram_id = message.chat.id

            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            path = post_service.salvar_foto_temporaria(downloaded_file)
            post_temp[telegram_id]["fotos"].append(path)

            bot.send_message(telegram_id, "✅ Foto adicionada.")

        except Exception as e:
            log.error(
                "Erro ao processar foto",
                extra={"telegram_id": telegram_id, "error": str(e)}
            )
            bot.send_message(
                telegram_id,
                "❌ Erro ao processar a foto."
            )
            post_temp.pop(telegram_id, None)

    # ------------------------------------------------------
    # Finalizar envio
    # ------------------------------------------------------

    @bot.callback_query_handler(func=lambda c: c.data == "post_finalizar_fotos")
    def finalizar_fotos(call):

        telegram_id = call.message.chat.id

        if post_temp.get(telegram_id, {}).get("estado") != POST_AGUARDANDO_FOTOS:
            return

        if not post_temp[telegram_id]["fotos"]:
            bot.answer_callback_query(call.id, "Envie pelo menos uma foto.")
            return

        gerar_post_final(bot, telegram_id, services)


# ==========================================================
# GERAÇÃO FINAL
# ==========================================================

def gerar_post_final(bot, telegram_id, services):

    post_service = services["post"]
    log = services["log"]

    data = post_temp.get(telegram_id)

    bot.send_message(telegram_id, "⏳ Gerando suas artes...")

    try:

        imagens = post_service.gerar_post(
            telegram_id=telegram_id,
            treino_id=data["treino_id"],
            fotos=data["fotos"],
            prompt_usuario=data["prompt"]
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
            f"Erro ao gerar post: \n{e}",
            extra={"telegram_id": telegram_id, "error": str(e)}
        )

        bot.send_message(
            telegram_id,
            "❌ Ocorreu um erro ao gerar o post."
        )

    finally:
        post_temp.pop(telegram_id, None)