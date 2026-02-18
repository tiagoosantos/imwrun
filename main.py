from utils.logging.log_config import HandlerConfig
from bot.telegram import create_bot
from wrapper import BotWrapper

APP_NAME = "Runner"
SETOR_NAME = "IMW"
APP = f"{SETOR_NAME}_{APP_NAME}"

def main():

    log_config = HandlerConfig(APP, email="gmail", long_running=True)
    log, email_handler = log_config.get_logger(APP)

    bot = create_bot(log)

    wrapper = BotWrapper(bot, log)
    wrapper.run()


if __name__ == "__main__":
    main()
