import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="c:/Users/x002426/.env")
# load_dotenv()

DB_HOST = os.getenv("DB183_HOST")
DB_PORT = os.getenv("DB183_PORT")
DB = os.getenv("DB183")
DB_USER = os.getenv("DB183_USER")
DB_PASS = os.getenv("DB183_PASS")

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

CRUE_DTIC_MAIL = ['bspaula@PREFEITURA.SP.GOV.BR', 
                  'drvrego@PREFEITURA.SP.GOV.BR', 
                  'leonardorondam@PREFEITURA.SP.GOV.BR', 
                  'simonebastos@PREFEITURA.SP.GOV.BR'
                  ]

DENGUE_SEM_EMAIL = ['mnakano@PREFEITURA.SP.GOV.BR',             # Maristela Uta Nakano
                    'smssuportesistemas@PREFEITURA.SP.GOV.BR',  # SMS - Suporte Sistemas
                    'simonebastos@PREFEITURA.SP.GOV.BR']        # Simone Santos Bastos

CARDIO_SEM_EMAIL = ['gfazzolari@PREFEITURA.SP.GOV.BR',          # Gislane Soares Fazzolari
                    'mnakano@PREFEITURA.SP.GOV.BR',             # José Carlos Ingrund
                    'jingrund@PREFEITURA.SP.GOV.BR',            # José Carlos Ingrund
                    'jhsegregio@PREFEITURA.SP.GOV.BR',          # Janio Henrique Segregio
                    'acepeda@PREFEITURA.SP.GOV.BR',             # Adelaide Alves Cepeda Felix
                    'smssuportesistemas@PREFEITURA.SP.GOV.BR',  # SMS - Suporte Sistemas
                    'simonebastos@PREFEITURA.SP.GOV.BR']        # Simone Santos Bastos

CARDIO_MEN_EMAIL = ['raquelporto@PREFEITURA.SP.GOV.BR',         # Raquel de Almeida Porto
                    'raporto@PREFEITURA.SP.GOV.BR',             # Raphaela Porto
                   'smssuportesistemas@PREFEITURA.SP.GOV.BR',   # SMS - Suporte Sistemas
                   'simonebastos@PREFEITURA.SP.GOV.BR']         # Simone Santos Bastos


PQ_MEN_EMAIL = ['adrianabrazao@PREFEITURA.SP.GOV.BR',           # Adriana Brazão Pileggi de Oliveira
                'apreturlan@PREFEITURA.SP.GOV.BR',              # Andréia Preturlan
                'smsredencao@PREFEITURA.SP.GOV.BR',             # SMS - SEABEVS - Redenção
                'cgoncalves@PREFEITURA.SP.GOV.BR',              # Carolina Della Monica Gonçalves
                'claudialonghi@PREFEITURA.SP.GOV.BR',           # Claudia Ruggiero Longhi
                'smssuportesistemas@PREFEITURA.SP.GOV.BR',      # SMS - Suporte Sistemas
                'simonebastos@PREFEITURA.SP.GOV.BR']            # Simone Santos Bastos

