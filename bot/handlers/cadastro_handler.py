from ia.gemini import responder_com_ia
from bot.keyboards.menu_keyboard import menu_principal


def register_cadastro(bot, services):

    usuario_service = services["usuario"]

    # =======================
    # VERIFICAÇÃO DE CADASTRO
    # =======================

    @bot.message_handler(func=lambda m: True)
    def verificar_cadastro(message):

        telegram_user = message.from_user
        telegram_id = telegram_user.id

        status = usuario_service.registrar_ou_atualizar(telegram_user)

        # =======================
        # SE ESTÁ AGUARDANDO NOME
        # =======================

        if status == "AGUARDANDO_NOME":

            nome = message.text.strip()

            if len(nome.split()) < 2:
                bot.send_message(
                    message.chat.id,
                    "❌ Informe *nome e sobrenome*.",
                    parse_mode="Markdown"
                )
                return

            usuario_service.salvar_nome(telegram_id, nome)

            bot.send_message(
                message.chat.id,
                f"✅ Cadastro concluído, *{nome}*!",
                parse_mode="Markdown"
            )

            # Envia menu após cadastro
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

            return

        # =======================
        # SE NÃO ESTÁ EM CADASTRO
        # =======================

        responder_com_ia(bot, message)
