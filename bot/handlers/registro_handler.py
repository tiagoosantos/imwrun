from datetime import date, datetime

from bot.state.registro_state import registro_temp, limpar_sessao
from bot.keyboards.menu_keyboard import menu_principal
from bot.keyboards.registro_keyboard import teclado_local
from bot.ui.calendar_builder import CalendarBuilder

from .registro_manual import iniciar_registro_manual
from .registro_foto import processar_foto
from service.registro_service import mostrar_resumo_final, confirmar_registro
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


# ==========================================
# 🔹 INSTÂNCIA GLOBAL DO CALENDÁRIO
# ==========================================

calendar_builder = CalendarBuilder(
    min_date=date(2020, 1, 1),   # ajuste se quiser limitar mais
    max_date=date.today(),
    start_hour=5,
    end_hour=22,
    interval_minutes=30,
)


# ==========================================
# 🔹 REGISTER REGISTRO
# ==========================================

def register_registro(bot, services):

    # --------------------------------------
    # /registrar
    # --------------------------------------

    @bot.message_handler(commands=["registrar"])
    def registrar(message):
        iniciar_registro_manual(bot, services, message)

    # --------------------------------------
    # FOTO
    # --------------------------------------

    @bot.message_handler(content_types=["photo"])
    def foto(message):
        processar_foto(bot, services, message)

    # --------------------------------------
    # TIPO
    # --------------------------------------

    @bot.callback_query_handler(func=lambda call: call.data.startswith("tipo_"))
    def callback_tipo(call):

        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id

        if chat_id not in registro_temp:
            bot.send_message(chat_id, "❌ Sessão expirada.")
            return

        registro_temp[chat_id]["tipo_treino"] = call.data.replace("tipo_", "")

        bot.send_message(
            chat_id,
            "📍 Onde foi realizado o treino?",
            reply_markup=teclado_local()
        )

    # --------------------------------------
    # LOCAL → ABRE CALENDÁRIO
    # --------------------------------------

    @bot.callback_query_handler(func=lambda call: call.data.startswith("local_"))
    def callback_local(call):

        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id

        if chat_id not in registro_temp:
            bot.send_message(chat_id, "❌ Sessão expirada.")
            return

        registro_temp[chat_id]["local_treino"] = call.data.replace("local_", "")

        hoje = date.today()

        markup = calendar_builder.build_calendar(
            hoje.year,
            hoje.month
        )

        # adiciona botão usar agora
        markup.add(
            InlineKeyboardButton(
                "⏩ Usar data e hora atual",
                callback_data="cal_now"
            )
        )

        bot.send_message(
            chat_id,
            "📅 Escolha a data do treino ou use a data atual:",
            reply_markup=markup
        )

    # --------------------------------------
    # NAVEGAÇÃO MÊS ANTERIOR
    # --------------------------------------

    @bot.callback_query_handler(func=lambda call: call.data.startswith("cal_prev_"))
    def callback_prev(call):

        bot.answer_callback_query(call.id)

        _, _, ano, mes = call.data.split("_")
        ano = int(ano)
        mes = int(mes)

        mes -= 1
        if mes < 1:
            mes = 12
            ano -= 1

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=calendar_builder.build_calendar(ano, mes)
        )

    # --------------------------------------
    # NAVEGAÇÃO MÊS POSTERIOR
    # --------------------------------------

    @bot.callback_query_handler(func=lambda call: call.data.startswith("cal_next_"))
    def callback_next(call):

        bot.answer_callback_query(call.id)

        _, _, ano, mes = call.data.split("_")
        ano = int(ano)
        mes = int(mes)

        mes += 1
        if mes > 12:
            mes = 1
            ano += 1

        bot.edit_message_reply_markup(
            call.message.chat.id,
            call.message.message_id,
            reply_markup=calendar_builder.build_calendar(ano, mes)
        )

    # --------------------------------------
    # SELEÇÃO DE DATA ATUAL
    # --------------------------------------

    @bot.callback_query_handler(func=lambda call: call.data == "cal_now")
    def callback_now(call):

        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id

        if chat_id not in registro_temp:
            bot.send_message(chat_id, "❌ Sessão expirada.")
            return

        registro_temp[chat_id]["data_corrida"] = datetime.now()

        mostrar_resumo_final(bot, services, chat_id)

    # --------------------------------------
    # SELEÇÃO DE DATA
    # --------------------------------------

    @bot.callback_query_handler(func=lambda call: call.data.startswith("cal_date_"))
    def callback_data(call):

        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id

        if chat_id not in registro_temp:
            bot.send_message(chat_id, "❌ Sessão expirada.")
            return

        _, _, ano, mes, dia = call.data.split("_")

        data_escolhida = date(int(ano), int(mes), int(dia))

        if data_escolhida > date.today():
            bot.send_message(chat_id, "❌ Não é permitido selecionar datas futuras.")
            return

        registro_temp[chat_id]["data_temp"] = data_escolhida

        msg = bot.send_message(
            chat_id,
            "🕒 Informe o horário no formato HH:MM\n\nExemplo: 06:30\n\nDigite 'sair' para cancelar."
        )

        bot.register_next_step_handler(
            msg,
            lambda m: registrar_hora_manual(bot, services, m)
        )

    # --------------------------------------
    # SELEÇÃO DE HORA
    # --------------------------------------

    @bot.callback_query_handler(func=lambda call: call.data.startswith("cal_time_"))
    def callback_time(call):

        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id

        if chat_id not in registro_temp:
            bot.send_message(chat_id, "❌ Sessão expirada.")
            return

        _, _, hora, minuto = call.data.split("_")

        data_base = registro_temp[chat_id]["data_temp"]

        data_final = datetime(
            data_base.year,
            data_base.month,
            data_base.day,
            int(hora),
            int(minuto),
        )

        # 🔒 Bloqueia horário futuro se for hoje
        if data_final > datetime.now():
            bot.send_message(chat_id, "❌ Não é permitido selecionar horário futuro.")
            return

        registro_temp[chat_id]["data_corrida"] = data_final
        del registro_temp[chat_id]["data_temp"]

        mostrar_resumo_final(bot, services, chat_id)

    # --------------------------------------
    # CONFIRMAR
    # --------------------------------------

    @bot.callback_query_handler(func=lambda call: call.data == "confirmar_registro")
    def callback_confirmar(call):

        bot.answer_callback_query(call.id)
        confirmar_registro(bot, services, call.message.chat.id)

    # --------------------------------------
    # CANCELAR
    # --------------------------------------

    @bot.callback_query_handler(func=lambda call: call.data == "cancelar_registro")
    def callback_cancelar(call):

        bot.answer_callback_query(call.id)
        limpar_sessao(call.message.chat.id)
        bot.send_message(call.message.chat.id, "❌ Registro cancelado.")

    # --------------------------------------
    # DECISÃO MANUAL (FOTO NÃO RECONHECIDA)
    # --------------------------------------

    @bot.callback_query_handler(
        func=lambda call: call.data in ["registro_manual_sim", "registro_manual_nao"]
    )
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

def registrar_hora_manual(bot, services, message):

    chat_id = message.chat.id
    log = services["log"]
    texto = message.text.strip()

    if chat_id not in registro_temp:
        bot.send_message(chat_id, "❌ Sessão expirada.")
        return

    if texto.lower() == "sair":
        limpar_sessao(chat_id)
        bot.send_message(chat_id, "❌ Registro cancelado.")
        return

    try:
        hora, minuto = map(int, texto.split(":"))

        if not (0 <= hora <= 23 and 0 <= minuto <= 59):
            raise ValueError

        data_base = registro_temp[chat_id]["data_temp"]

        data_final = datetime(
            data_base.year,
            data_base.month,
            data_base.day,
            hora,
            minuto
        )

        # 🔒 Bloqueia horário futuro se for hoje
        if data_final > datetime.now():
            bot.send_message(
                chat_id,
                "❌ Não é permitido registrar horário futuro."
            )
            bot.register_next_step_handler(
                message,
                lambda m: registrar_hora_manual(bot, services, m)
            )
            return

        registro_temp[chat_id]["data_corrida"] = data_final
        del registro_temp[chat_id]["data_temp"]

        log.info(
            "Data e hora registradas manualmente",
            extra={
                "telegram_id": chat_id,
                "data_corrida": data_final.isoformat()
            }
        )

        mostrar_resumo_final(bot, services, chat_id)

    except Exception:
        bot.send_message(
            chat_id,
            "❌ Formato inválido.\n\nUse HH:MM\nExemplo: 06:30"
        )
        bot.register_next_step_handler(
            message,
            lambda m: registrar_hora_manual(bot, services, m)
        )