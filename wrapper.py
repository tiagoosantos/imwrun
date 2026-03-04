import time
import logging
import traceback


class BotWrapper:

    def __init__(self, bot, logger: logging.Logger):
        self.bot = bot
        self.logger = logger

    def run(self):
        self.logger.info("🚀 Iniciando bot de corrida")

        while True:
            try:
                self.bot.infinity_polling(
                    timeout=20,
                    long_polling_timeout=50
                )

            except Exception as e:
                # self.logger.error(
                #     "Erro crítico no bot",
                #     extra={
                #         "erro": str(e),
                #         "traceback": traceback.format_exc(),
                #     },
                # )

                # self.logger.info("🔄 Reiniciando bot em 5 segundos...")
                # time.sleep(5)
                self.logger.warning('Polling reiniciando...')
