from telebot import TeleBot
from config.settings import BOT_TOKEN, GEMINI
from database.connection import init_pool

from service.corrida_service import CorridaService
from service.usuario_service import UsuarioService
from service.relatorio_service import RelatorioService
from service.vision_service import TreinoVisionService

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

    # conn = get_connection()
    init_pool(minconn=1, maxconn=20)

    # =======================
    # SERVICES
    # =======================

    services = {
        "usuario": UsuarioService(),
        "corrida": CorridaService(),
        "relatorio": RelatorioService(),
        "vision": TreinoVisionService(GEMINI),
        "log": log,
    }

    # =======================
    # REGISTRO DE HANDLERS
    # =======================

    register_handlers(bot, services)

    log.info("Bot Telegram configurado com sucesso")

    return bot
