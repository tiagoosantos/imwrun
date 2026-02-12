from bot.telegram import iniciar_bot, email_handler, log

if __name__ == "__main__":
    try:
        iniciar_bot()
    except KeyboardInterrupt:
        log.warning("Bot interrompido manualmente")
    except Exception:
        log.exception("Falha crítica no bot")
    finally:
        if email_handler:
            email_handler.flush()