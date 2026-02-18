# from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.keyboards.menu_keyboard import menu_principal
from bot.handlers.registro_handler import registrar_command


def register_start(bot, services):

    usuario_service = services["usuario"]
    log = services["log"]

    # ==========================================================
    # FUNÇÃO REUTILIZÁVEL PARA ENVIAR MENU
    # ==========================================================

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

    # ==========================================================
    # /start
    # ==========================================================

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

    # ==========================================================
    # CALLBACK MENU PRINCIPAL
    # ==========================================================

    @bot.callback_query_handler(func=lambda call: call.data.startswith("cmd_"))
    def callbacks(call):

        bot.answer_callback_query(call.id)

        chat_id = call.message.chat.id

        # Aqui NÃO usamos fake_message
        # Apenas enviamos o comando normalmente

        if call.data == "cmd_registrar":
            registrar_command(bot, services, call.message)

        elif call.data == "cmd_ranking_km":
            bot.send_message(chat_id, "/ranking_km")

        elif call.data == "cmd_pace":
            bot.send_message(chat_id, "/pace")

        elif call.data == "cmd_relatorio":
            bot.send_message(chat_id, "/relatorio")
