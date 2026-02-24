from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto
)
from bot.state.post_state import post_temp

# ==========================
# ESTADOS
# ==========================

POST_AGUARDANDO_FOTOS = "post_aguardando_fotos"
POST_ESCOLHENDO_TREINO = "post_escolhendo_treino"
POST_ESCOLHENDO_PROMPT = "post_escolhendo_prompt"
POST_AGUARDANDO_PROMPT_CUSTOM = "post_aguardando_prompt_custom"


# ==========================
# INICIO
# ==========================

def iniciar_post_command(bot, services, message):

    post_service = services["post"]
    log = services["log"]

    telegram_id = message.chat.id
    correlation_id = message.message_id

    log.info(
        "Iniciando fluxo de postar treino",
        extra={"telegram_id": telegram_id, "correlation_id": correlation_id}
    )

    if not post_service.pode_gerar_post(telegram_id):
        bot.send_message(
            telegram_id,
            "⚠️ Você já utilizou suas 2 gerações hoje.\nTente novamente amanhã."
        )
        return

    post_temp[telegram_id] = {
    "estado": POST_AGUARDANDO_FOTOS,
    "fotos": [],
    "treino_id": None,
    "prompt": None
}

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "✅ Finalizar envio",
            callback_data="post_finalizar_fotos"
        )
    )

    bot.send_message(
        telegram_id,
        "📸 Envie uma ou mais fotos.\nQuando terminar, clique em Finalizar.",
        reply_markup=markup
    )

# ==========================
# REGISTRO DO HANDLER
# ==========================

def register_post(bot, services):

    post_service = services["post"]
    corrida_service = services["corrida"]
    log = services["log"]

    # ==========================
    # INICIAR POST (via menu callback)
    # ==========================

    @bot.callback_query_handler(func=lambda c: c.data == "cmd_postar")
    def iniciar_post_callback(call):

        bot.answer_callback_query(call.id)
        iniciar_post_command(bot, services, call.message)

        telegram_id = call.message.chat.id
        correlation_id = call.message.message_id

        log.info(
            "Iniciando fluxo de postar treino",
            extra={"telegram_id": telegram_id, "correlation_id": correlation_id}
        )

        if not post_service.pode_gerar_post(telegram_id):
            bot.send_message(
                telegram_id,
                "⚠️ Você já utilizou suas 2 gerações hoje.\nTente novamente amanhã."
            )
            return

        post_temp[telegram_id] = {
            "estado": POST_AGUARDANDO_FOTOS,
            "fotos": [],
            "treino_id": None,
            "prompt": None
        }

        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton(
                "✅ Finalizar envio",
                callback_data="post_finalizar_fotos"
            )
        )

        bot.send_message(
            telegram_id,
            "📸 Envie uma ou mais fotos.\nQuando terminar, clique em Finalizar.",
            reply_markup=markup
        )

    # ==========================
    # RECEBER FOTOS
    # ==========================

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
            bot.send_message(message.chat.id, f"❌ Erro ao processar foto: {e}")
            post_temp.pop(telegram_id, None)
            log.error(
                "Erro ao processar foto",
                extra={"telegram_id": message.chat.id, "error": str(e)}
            )
    # ==========================
    # FINALIZAR FOTOS
    # ==========================

    @bot.callback_query_handler(func=lambda c: c.data == "post_finalizar_fotos")
    def finalizar_fotos(call):
        try:
            telegram_id = call.message.chat.id

            if post_temp.get(telegram_id, {}).get("estado") != POST_AGUARDANDO_FOTOS:
                return

            data = post_temp.get(telegram_id, {})

            if not data["fotos"]:
                bot.answer_callback_query(call.id, "Envie pelo menos uma foto.")
                return

            treinos = corrida_service.listar_ultimos(telegram_id)

            if not treinos:
                bot.send_message(telegram_id, "Você ainda não possui treinos registrados.")
                return

            markup = InlineKeyboardMarkup()

            for treino in treinos:
                markup.add(
                    InlineKeyboardButton(
                        f"{treino.distancia_metros/1000:.2f}km - {treino.tempo_formatado}",
                        callback_data=f"post_treino_{treino.id}"
                    )
                )

            post_temp[telegram_id]["estado"] = POST_ESCOLHENDO_TREINO

            bot.edit_message_text(
                "🏃 Escolha o treino para gerar o post:",
                telegram_id,
                call.message.message_id,
                reply_markup=markup
            )
        except Exception as e:
            log.error(
                "Erro ao finalizar fotos",
                extra={"telegram_id": call.message.chat.id, "error": str(e)}
            )
            bot.send_message(call.message.chat.id, f"❌ Erro: {e}")
            post_temp.pop(telegram_id, None)
        finally:
            post_temp.pop(telegram_id, None)

    # ==========================
    # ESCOLHER TREINO
    # ==========================

    @bot.callback_query_handler(func=lambda c: c.data.startswith("post_treino_"))
    def escolher_treino(call):

        telegram_id = call.message.chat.id

        if post_temp.get(telegram_id, {}).get("estado") != POST_ESCOLHENDO_TREINO:
            return

        treino_id = int(call.data.split("_")[-1])

        data = post_temp.get(telegram_id, {})
        data["treino_id"] = treino_id
        post_temp[telegram_id] = data

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

        post_temp[telegram_id]["estado"] = POST_ESCOLHENDO_PROMPT

        bot.edit_message_text(
            "🎨 Escolha o estilo do post:",
            telegram_id,
            call.message.message_id,
            reply_markup=markup
        )

    # ==========================
    # ESCOLHER PROMPT MODELO
    # ==========================

    @bot.callback_query_handler(func=lambda c: c.data.startswith("post_prompt_"))
    def escolher_prompt(call):

        telegram_id = call.message.chat.id

        if post_temp.get(telegram_id, {}).get("estado") != POST_ESCOLHENDO_PROMPT:
            return

        if call.data == "post_prompt_custom":
            post_temp[telegram_id]["estado"] = POST_AGUARDANDO_PROMPT_CUSTOM
            bot.send_message(telegram_id, "✍️ Envie o prompt que deseja utilizar:")
            return

        prompt_key = call.data.replace("post_prompt_", "")

        prompt = post_service.obter_prompt_modelo(prompt_key)

        data = post_temp.get(telegram_id, {})
        data["prompt"] = prompt
        post_temp[telegram_id] = data

        gerar_post_final(bot, telegram_id, services)

    # ==========================
    # RECEBER PROMPT CUSTOM
    # ==========================

    @bot.message_handler(func=lambda m: True)
    def receber_prompt_custom(message):

        telegram_id = message.chat.id

        if post_temp.get(telegram_id, {}).get("estado") != POST_AGUARDANDO_PROMPT_CUSTOM:
            return

        data = post_temp.get(telegram_id, {})
        data["prompt"] = message.text
        post_temp[telegram_id] = data

        gerar_post_final(bot, telegram_id, services)


# ==========================
# FUNÇÃO FINAL DE GERAÇÃO
# ==========================

def gerar_post_final(bot, telegram_id, services):

    post_service = services["post"]
    log = services["log"]

    data = post_temp.get(telegram_id, {})

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

        # fechar arquivos
        for m in media:
            m.media.close()

        post_service.limpar_arquivos(imagens)

        post_temp.pop(telegram_id, None)

    except Exception as e:

        log.error(
            "Erro ao gerar post",
            extra={"telegram_id": telegram_id}
        )

        bot.send_message(
            telegram_id,
            "❌ Ocorreu um erro ao gerar o post. Tente novamente."
        )

        post_temp.pop(telegram_id, None)