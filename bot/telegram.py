from telebot import TeleBot
from config.settings import BOT_TOKEN
from database.connection import get_connection

from service.corrida_service import CorridaService
from service.usuario_service import UsuarioService
from service.relatorio_service import RelatorioService

from bot.handlers import register_handlers


def create_bot(log):
    """
    Cria e configura o bot Telegram.
    Recebe o logger já configurado pelo main.
    """

    # =======================
    # INSTÂNCIA DO BOT
    # =======================

    bot = TeleBot(BOT_TOKEN)

    # =======================
    # CONEXÃO BANCO
    # =======================

    conn = get_connection()

    # =======================
    # SERVICES
    # =======================

    services = {
        "usuario": UsuarioService(conn),
        "corrida": CorridaService(),
        "relatorio": RelatorioService(),
        "log": log,
    }

    # =======================
    # REGISTRO DE HANDLERS
    # =======================

    register_handlers(bot, services)

    log.info("Bot Telegram configurado com sucesso")

    return bot
