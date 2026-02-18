from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.menu_keyboard import menu_principal


def register_start(bot, services):

    usuario_service = services["usuario"]
    log = services["log"]

    # =======================
    # /start
    # =======================

    @bot.message_handler(commands=["start"])
    def start(message):

        correlation_id = message.message_id
        telegram_user = message.from_user
        telegram_id = telegram_user.id

        status = usuario_service.registrar_ou_atualizar(telegram_user)

        log.info(
            "Comando /start",
            extra={
                "telegram_id": telegram_id,
                "correlation_id": correlation_id,
                "status_usuario": status,
            },
        )

        if status == "AGUARDANDO_NOME":
            bot.send_message(
                message.chat.id,
                "👋 Olá! Antes de começarmos, me diga seu *nome completo*:",
                parse_mode="Markdown"
            )
            return

        enviar_menu_principal(message)

    # =======================
    # MENU PRINCIPAL
    # =======================

    def enviar_menu_principal(message):

        texto = (
            "🏃 *Bem-vindo ao IMW Runner!*\n\n"
            "Aqui você registra treinos e acompanha rankings de corrida.\n\n"
            "*Escolha uma ação:*"
        )

        bot.send_message(
            message.chat.id,
            texto,
            reply_markup=menu_principal(),
            parse_mode="Markdown",
        )

    # =======================
    # CALLBACK MENU
    # =======================

    @bot.callback_query_handler(func=lambda call: call.data.startswith("cmd_"))
    def callbacks(call):

        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id
        user = call.from_user

        comandos = {
            "cmd_registrar": "/registrar",
            "cmd_ranking_km": "/ranking_km",
            "cmd_pace": "/pace",
            "cmd_relatorio": "/relatorio",
        }

        func = comandos.get(call.data)

        if func:
            func(call.message)

        if not func:
            return

        # # cria uma mensagem fake para reaproveitar handlers existentes
        # fake_message = call.message
        # fake_message.text = comando
        # fake_message.from_user = user
        # fake_message.chat = call.message.chat

        # bot.process_new_messages([fake_message])
