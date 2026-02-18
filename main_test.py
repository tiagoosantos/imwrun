from utils.logging.log_config import HandlerConfig
from bot.telegram import create_bot

APP = "IMW_Runner_TEST"

if __name__ == "__main__":
    log_config = HandlerConfig(APP, email=None)
    log, email_handler = log_config.get_logger(APP)

    try:
        bot = create_bot(log)
        bot.infinity_polling()
        log.info("Bot iniciado em modo TESTE")

    except KeyboardInterrupt:
        log.warning("Bot interrompido manualmente")

    except Exception:
        log.exception("Falha crítica no bot")

    finally:
        if email_handler:
            email_handler.flush()
