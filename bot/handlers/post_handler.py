from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto
)
import threading
from concurrent.futures import ThreadPoolExecutor
from bot.state.post_state import post_temp, post_timers
from bot.utils.bot_utils import formatar_tempo, formatar_distancia


# ==========================================================
# EXECUTOR PARA BACKGROUND
# ==========================================================

executor = ThreadPoolExecutor(max_workers=3)


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

        # bot.edit_message_text(
        #     "📸 Agora envie uma foto para gerar o post.",
        #     telegram_id,
        #     call.message.message_id
        # )

        bot.send_message(
            telegram_id,
            "📸 Agora envie uma foto para gerar o post.",
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

        if data.get("gerando"):
            bot.send_message(
                telegram_id,
                "⏳ Já estou gerando um post para você, aguarde."
            )
            return

        correlation_id = data["correlation_id"]

        try:

            file_info = bot.get_file(message.photo[-1].file_id)
            downloaded_file = bot.download_file(file_info.file_path)

            path = post_service.salvar_foto_temporaria(downloaded_file)

            data["foto"] = path
            data["gerando"] = True

            log.info(
                "Foto recebida para gerar post",
                extra={
                    "telegram_id": telegram_id,
                    "correlation_id": correlation_id
                }
            )

            bot.send_message(telegram_id, "⏳ Gerando seu post...")
            bot.send_chat_action(telegram_id, "upload_photo")

            # 🔥 EXECUTA EM BACKGROUND
            executor.submit(
                gerar_post_final,
                bot,
                telegram_id,
                services
            )

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
            
    # ------------------------------------------------------
    # Cancelar apenas fluxo de post
    # ------------------------------------------------------

    @bot.message_handler(commands=["cancelar"])
    def cancelar_post(message):

        telegram_id = message.chat.id
        data = post_temp.get(telegram_id)

        # 🔎 Só cancela se houver post em andamento
        if not data:
            bot.send_message(
                telegram_id,
                "ℹ️ Nenhum post em andamento para cancelar."
            )
            return

        # 🔒 Cancelar timer se existir
        timer = post_timers.pop(telegram_id, None)
        if timer:
            timer.cancel()

        # 🔒 Limpar estado
        post_temp.pop(telegram_id, None)

        bot.send_message(
            telegram_id,
            "❌ Geração de post cancelada com sucesso."
        )

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

    try:

        bot.send_message(telegram_id, "👍 Tá pronto o seu post...")

        resultado = post_service.gerar_post(
            telegram_id=telegram_id,
            treino_id=data["treino_id"],
            fotos=[data["foto"]]
        )

        # 🔒 Se atingiu limite por minuto
        if isinstance(resultado, dict) and resultado.get("aguardar"):

            segundos = resultado["segundos"]

            bot.send_message(
                telegram_id,
                f"🚦 Muitas solicitações no momento.\n"
                f"Aguardando {segundos} segundos para tentar novamente..."
            )

            # Cancelar timer antigo se existir
            timer_existente = post_timers.get(telegram_id)
            if timer_existente:
                timer_existente.cancel()

            # Criar novo timer
            timer = threading.Timer(
                segundos,
                gerar_post_final,
                args=(bot, telegram_id, services)
            )

            post_timers[telegram_id] = timer
            timer.start()

            return  # ⚠️ IMPORTANTE: não limpar estado aqui

        imagens = resultado

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

        # post_service.limpar_arquivos(imagens)

        # 🔥 Limpeza final segura
        post_temp.pop(telegram_id, None)

        timer = post_timers.pop(telegram_id, None)
        if timer:
            timer.cancel()

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

        post_temp.pop(telegram_id, None)

        timer = post_timers.pop(telegram_id, None)
        if timer:
            timer.cancel()
    