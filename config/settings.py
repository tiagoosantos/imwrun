import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="c:/Users/x002426/.env")
# load_dotenv()

IMW_HOST = os.getenv("IMW_HOST")
IMW_PORT = os.getenv("IMW_PORT")
IMW_DB = os.getenv("IMW_DB")
IMW_USER = os.getenv("IMW_USER")
IMW_PASS = os.getenv("IMW_PASS")

BOT_TOKEN = os.getenv("BOT_IMWRUNNER")
CHAT_ID = os.getenv("CHAT_ID")
GROUP_ID = os.getenv("GROUP_ID")

BOT_TESTE_TOKEN = os.getenv("TELEBOT_TESTE_IA")
GEMINI = os.getenv("GEMINI_TOKEN")

USER_NOX = os.getenv("smtp_username_nox")
PASS_NOX = os.getenv("smtp_password_nox")
SERVER_NOX = os.getenv("smtp_server_nox")
PORT_NOX = os.getenv("smtp_port_nox")
SENDER_NOX = os.getenv("sender_nox")

USER_PRODAM = os.getenv("smtp_user_prodam")
PASS_PRODAM = os.getenv("smtp_password_prodam")
SERVER_PRODAM = os.getenv("smtp_server_prodam")
PORT_PRODAM = os.getenv("smtp_port_prodam")
SENDER_PRODAM = os.getenv("sender_prodam")

USER_GMAIL = os.getenv("user_gmail")
SENDER_GMAIL = os.getenv("sender_gmail")
PASSWORD_GMAIL = os.getenv("smtp_password_gmail")
SERVER_GMAIL = os.getenv("smtp_server_gmail")
PORT_GMAIL = os.getenv("smtp_port_gmail")

