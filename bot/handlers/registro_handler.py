from datetime import datetime
from bot.state.registro_state import registro_temp, limpar_sessao
from bot.keyboards.menu_keyboard import menu_principal
from bot.keyboards.registro_keyboard import teclado_local
from bot.utils.bot_utils import usuario_cancelou
from .registro_manual import iniciar_registro_manual
from .registro_foto import processar_foto
from service.registro_service import mostrar_resumo_final, confirmar_registro


def register_registro(bot, services):

    @bot.message_handler(commands=["registrar"])
    def registrar(message):
        iniciar_registro_manual(bot, services, message)

    @bot.message_handler(content_types=["photo"])
    def foto(message):
        processar_foto(bot, services, message)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("tipo_"))
    def callback_tipo(call):
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        if chat_id not in registro_temp:
            bot.send_message(chat_id, "❌ Sessão expirada.")
            return
        tipo = call.data.replace("tipo_", "")
        registro_temp[chat_id]["tipo_treino"] = tipo
        bot.send_message(chat_id, "📍 Onde foi realizado o treino?", reply_markup=teclado_local())

    @bot.callback_query_handler(func=lambda call: call.data.startswith("local_"))
    def callback_local(call):
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        if chat_id not in registro_temp:
            bot.send_message(chat_id, "❌ Sessão expirada.")
            return
        registro_temp[chat_id]["local_treino"] = call.data.replace("local_", "")
        bot.send_message(chat_id, "Digite a data no formato DD/MM/AAAA HH:MM ou 'pular'")
        bot.register_next_step_handler(call.message, lambda m: registrar_data(bot, services, m))

    @bot.callback_query_handler(func=lambda call: call.data in ["registro_manual_sim", "registro_manual_nao"])
    def callback_registro_manual(call):

        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id

        if call.data == "registro_manual_sim":
            iniciar_registro_manual(bot, services, call.message)

        else:
            bot.send_message(
                chat_id,
                "Foi mal, vou tentar melhorar nos próximos updates.\n\n"
                "Se quiser tentar novamente, envie outra imagem."
            )

            bot.send_message(
                chat_id,
                "\nSe preferir, pode me perguntar o que quiser sobre o mundo da corrida "
                "ou dar uma olhada nas outras funções que fiz pra vc",
                reply_markup=menu_principal(),
                parse_mode="Markdown",
            )

def registrar_data(bot, services, message):

    chat_id = message.chat.id
    texto = message.text.strip()
    log = services["log"]

    if usuario_cancelou(texto):
        limpar_sessao(chat_id)
        bot.send_message(chat_id, "❌ Registro cancelado.")
        log.info(
            "Registro cancelado via texto",
            extra={"telegram_id": chat_id}
        )
        return

    if texto.lower() == "pular":
        if chat_id not in registro_temp:
            bot.send_message(chat_id, "❌ Sessão expirada.")
            return
        registro_temp[chat_id]["data_corrida"] = None
    else:
        try:
            data_convertida = datetime.strptime(texto, "%d/%m/%Y %H:%M")
            if chat_id not in registro_temp:
                bot.send_message(chat_id, "❌ Sessão expirada.")
                return
            registro_temp[chat_id]["data_corrida"] = data_convertida
        except ValueError:
            bot.send_message(
                chat_id,
                "❌ Formato inválido.\n\nUse: DD/MM/AAAA HH:MM\nOu digite 'pular'."
            )
            bot.register_next_step_handler(
                message,
                lambda m: registrar_data(bot, services, m)
            )
            return

    mostrar_resumo_final(bot, services, chat_id)

    @bot.callback_query_handler(func=lambda call: call.data == "confirmar_registro")
    def callback_confirmar(call):
        bot.answer_callback_query(call.id)
        confirmar_registro(bot, services, call.message.chat.id)

    @bot.callback_query_handler(func=lambda call: call.data == "cancelar_registro")
    def callback_cancelar(call):
        bot.answer_callback_query(call.id)
        limpar_sessao(call.message.chat.id)
        bot.send_message(call.message.chat.id, "❌ Registro cancelado.")