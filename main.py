from bot.telegram import bot
from wrapper import BotWrapper
from utils.logging.log_config import HandlerConfig

APP_NAME = "Runner"
SETOR_NAME = "IMW"
APP = f"{SETOR_NAME}_{APP_NAME}"

log_config = HandlerConfig(APP, email="gmail", long_running=True)
log, email_handler = log_config.get_logger(APP)


def main():
    logger = log

    wrapper = BotWrapper(
        bot=bot,
        logger=logger
    )

    wrapper.run()


if __name__ == "__main__":
    main()
