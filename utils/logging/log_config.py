# v5_log_config.py
import logging
import os
import smtplib
import telebot

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

from config.settings import BOT_TOKEN, CHAT_ID, GROUP_ID

from utils.logging.log_handlers import (
    BatchEmailHandler_gmail,
    BatchEmailHandler_nox,
    BatchEmailHandler_prodam,
    TelegramHandler,
    get_file_handler,   # 👈 NOVO
)

# =======================
# HANDLER CONFIG (GERAL)
# =======================

class HandlerConfig:
    def __init__(
        self,
        app_name: str,
        email: str = None,
        long_running: bool = False,   # 👈 NOVO
    ):
        self.app_name = app_name
        self.email = email if email else 'nox'
        self.long_running = long_running
        self.email_handler = None

    def get_logger(self, logger_name: str, return_email_handler: bool = True):

        log = logging.getLogger(logger_name)
        log.setLevel(logging.INFO)

        if not log.handlers:

            formatter = logging.Formatter(
                f'LOG_{logger_name.upper()} %(asctime)s - %(levelname)s - %(message)s'
            )

            formatter_chat = logging.Formatter(
                f'LOG_{logger_name.upper()} %(asctime)s - %(levelname)s \n%(message)s'
            )

            # =======================
            # FILE HANDLER (batch ou bot)
            # =======================

            file_handler = get_file_handler(
                self.app_name,
                long_running=self.long_running,
            )
            file_handler.setFormatter(formatter)
            file_handler.setLevel(logging.INFO)
            log.addHandler(file_handler)

            # =======================
            # CONSOLE
            # =======================

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            console_handler.setLevel(logging.INFO)
            log.addHandler(console_handler)

            # =======================
            # EMAIL
            # =======================

            if self.email == 'gmail':
                self.email_handler = BatchEmailHandler_gmail(app_name=logger_name)
            elif self.email == 'prodam':
                self.email_handler = BatchEmailHandler_prodam(app_name=logger_name)
            else:
                self.email_handler = BatchEmailHandler_nox(app_name=logger_name)

            self.email_handler.setFormatter(formatter)
            self.email_handler.setLevel(logging.ERROR)
            log.addHandler(self.email_handler)

            # =======================
            # TELEGRAM (CHAT)
            # =======================

            telegram_chat_handler = TelegramHandler(BOT_TOKEN, CHAT_ID)
            telegram_chat_handler.setFormatter(formatter_chat)
            telegram_chat_handler.setLevel(logging.ERROR)
            log.addHandler(telegram_chat_handler)

            # =======================
            # TELEGRAM (GRUPO – opcional)
            # =======================

            telegram_group_handler = TelegramHandler(BOT_TOKEN, GROUP_ID)
            telegram_group_handler.setFormatter(formatter_chat)
            telegram_group_handler.setLevel(logging.CRITICAL)
            # log.addHandler(telegram_group_handler)

            log.propagate = False

        if return_email_handler:
            return log, self.email_handler
        return log

    # =======================
    # EMAIL COM ANEXOS
    # =======================

    def send_email_with_attachments(
        self,
        subject: str,
        body: str,
        recipients: list,
        attachments: list = None,
        app_name: str = None,
        email: str = None,
    ):

        if not self.email_handler:
            logging.getLogger(__name__).error("Email handler not initialized.")
            return

        sender = self.email_handler.sender
        smtp_server = self.email_handler.smtp_server
        smtp_port = self.email_handler.smtp_port
        smtp_user = self.email_handler.smtp_username
        smtp_password = getattr(self.email_handler, 'smtp_password', None)

        try:
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = ", ".join(recipients)
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            if attachments:
                for filepath in attachments:
                    if os.path.isfile(filepath) and app_name in filepath:
                        with open(filepath, "rb") as f:
                            part = MIMEApplication(
                                f.read(),
                                Name=os.path.basename(filepath),
                            )
                            part['Content-Disposition'] = (
                                f'attachment; filename="{os.path.basename(filepath)}"'
                            )
                            msg.attach(part)

            if self.email == 'prodam':
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.sendmail(sender, recipients, msg.as_string())
            else:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_password)
                    server.sendmail(sender, recipients, msg.as_string())

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao enviar e-mail com anexos: {e}")

    # =======================
    # ENVIO DE ARQUIVOS TELEGRAM
    # =======================

    def send_files_telebot(self, file_path: list, app_name, group: bool = True):
        bot = telebot.TeleBot(BOT_TOKEN)
        chat_id = GROUP_ID if group else CHAT_ID

        try:
            for file in file_path:
                if os.path.isfile(file) and app_name in file:
                    with open(file, 'rb') as f:
                        bot.send_document(chat_id, f)
                else:
                    logging.getLogger(__name__).error(f"Arquivo não encontrado: {file}")
        except Exception as e:
            logging.getLogger(__name__).error(
                f"Erro ao enviar arquivo para o Telegram: {e}"
            )

# =======================
# HANDLER CONFIG TELEBOT
# =======================

class HandlerConfig_telebot(HandlerConfig):
    def __init__(self, app_name: str, email: str = None):
        super().__init__(
            app_name=app_name,
            email=email,
            long_running=True,   # 👈 SEMPRE BOT
        )
