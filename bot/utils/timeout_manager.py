import threading
from bot.state.registro_state import registro_temp, limpar_sessao


timers = {}


def iniciar_timeout(bot, chat_id, segundos=90):

    cancelar_timeout(chat_id)

    timer = threading.Timer(
        segundos,
        lambda: timeout_callback(bot, chat_id)
    )

    timers[chat_id] = timer
    timer.start()


def cancelar_timeout(chat_id):

    timer = timers.pop(chat_id, None)
    if timer:
        timer.cancel()


def timeout_callback(bot, chat_id):

    if chat_id in registro_temp:
        limpar_sessao(chat_id)
        bot.send_message(
            chat_id,
            "⏳ Registro cancelado por não ter recebido resposta em 1 minuto."
        )