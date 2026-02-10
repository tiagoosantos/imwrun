#%% IMPORTS
# v5_log_handlers.py
import logging
from logging.handlers import TimedRotatingFileHandler
import smtplib
from email.mime.text import MIMEText
import telebot
import os

from config.settings import (
    USER_NOX, PASS_NOX, SERVER_NOX, PORT_NOX, SENDER_NOX,
    USER_PRODAM, PASS_PRODAM, SERVER_PRODAM, PORT_PRODAM, SENDER_PRODAM,
    USER_GMAIL, SENDER_GMAIL, PASSWORD_GMAIL, SERVER_GMAIL, PORT_GMAIL
)

# =======================
# BASE DIR
# =======================

BASE_LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(BASE_LOG_DIR, exist_ok=True)

# =======================
# FILE HANDLER
# =======================

def get_file_handler(app_name: str, long_running: bool = False):
    log_path = os.path.join(BASE_LOG_DIR, f"{app_name}.log")

    if long_running:
        handler = TimedRotatingFileHandler(
            filename=log_path,
            when="midnight",
            interval=1,
            backupCount=14,      # mantém 14 dias
            encoding="utf-8",
            utc=False,
        )
        handler.suffix = "%Y-%m-%d"
    else:
        handler = logging.FileHandler(
            filename=log_path,
            encoding="utf-8",
        )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s | "
        "telegram_id=%(telegram_id)s correlation_id=%(correlation_id)s"
    )

    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    return handler

# =======================
# EMAIL – NOXTEC
# =======================

class BatchEmailHandler_nox(logging.Handler):
    def __init__(self, app_name=None, recipients=None):
        super().__init__()
        self.errors = []
        self.app_name = app_name or "aplicação não informada"

        self.smtp_username = USER_NOX
        self.smtp_password = PASS_NOX
        self.smtp_server = SERVER_NOX
        self.smtp_port = PORT_NOX
        self.sender = SENDER_NOX
        self.recipients = recipients or ['tiagoosantos@prefeitura.sp.gov.br']

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.errors.append(self.format(record))

    def flush(self):
        if not self.errors:
            return

        message = "\n\n".join(self.errors)
        subject = f"[ERROS - {self.app_name}] {len(self.errors)} problemas detectados"

        try:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = ", ".join(self.recipients)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.sender, self.recipients, msg.as_string())

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao enviar e-mail de erro: {e}")
        finally:
            self.errors.clear()

# =======================
# EMAIL – PRODAM
# =======================

class BatchEmailHandler_prodam(logging.Handler):
    def __init__(self, app_name=None, recipients=None):
        super().__init__()
        self.errors = []
        self.app_name = app_name or "aplicação não informada"

        self.smtp_username = USER_PRODAM
        self.smtp_password = PASS_PRODAM
        self.smtp_server = SERVER_PRODAM
        self.smtp_port = PORT_PRODAM
        self.sender = SENDER_PRODAM
        self.recipients = recipients or ['tiagoosantos@prefeitura.sp.gov.br']

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.errors.append(self.format(record))

    def flush(self):
        if not self.errors:
            return

        message = "\n\n".join(self.errors)
        subject = f"[ERROS - {self.app_name}] {len(self.errors)} problemas detectados"

        try:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = ", ".join(self.recipients)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.sendmail(self.sender, self.recipients, msg.as_string())

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao enviar e-mail de erro: {e}")
        finally:
            self.errors.clear()

# =======================
# EMAIL – GMAIL
# =======================

class BatchEmailHandler_gmail(logging.Handler):
    def __init__(self, app_name=None, recipients=None):
        super().__init__()
        self.errors = []
        self.app_name = app_name or "aplicação não informada"

        self.smtp_username = USER_GMAIL
        self.smtp_password = PASSWORD_GMAIL
        self.smtp_server = SERVER_GMAIL
        self.smtp_port = PORT_GMAIL
        self.sender = SENDER_GMAIL
        self.recipients = recipients or ['tiagoosantos@prefeitura.sp.gov.br']

    def emit(self, record):
        if record.levelno >= logging.ERROR:
            self.errors.append(self.format(record))

    def flush(self):
        if not self.errors:
            return

        message = "\n\n".join(self.errors)
        subject = f"[ERROS - {self.app_name}] {len(self.errors)} problemas detectados"

        try:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.sender
            msg['To'] = ", ".join(self.recipients)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.sender, self.recipients, msg.as_string())

        except Exception as e:
            logging.getLogger(__name__).error(f"Erro ao enviar e-mail de erro: {e}")
        finally:
            self.errors.clear()

# =======================
# TELEGRAM HANDLER (OPCIONAL)
# =======================

class TelegramHandler(logging.Handler):
    def __init__(self, bot_token, chat_id, level=logging.ERROR):
        super().__init__(level)
        self.chat_id = chat_id
        self.bot = telebot.TeleBot(bot_token, parse_mode=None)

    def emit(self, record):
        try:
            log_entry = self.format(record)
            self.bot.send_message(self.chat_id, log_entry)
        except Exception:
            self.handleError(record)
