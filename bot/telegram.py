from telebot import TeleBot

from config.settings import BOT_TOKEN, GEMINI
from database.connection import init_pool

from service.usuario_service import UsuarioService
from service.corrida_service import CorridaService
from service.relatorio_service import RelatorioService
from service.vision_service import TreinoVisionService
from service.post_service import PostService

from repository.post_repository import PostRepository

from ia.gemini import GeminiClient
from ia.post_generator import PostGenerator

from bot.handlers import register_handlers


def create_bot(log):

    # ==========================
    # BOT
    # ==========================
    bot = TeleBot(BOT_TOKEN)

    # ==========================
    # POOL DE CONEXÕES
    # ==========================
    init_pool(minconn=1, maxconn=20)

    # ==========================
    # GEMINI
    # ==========================
    gemini_client = GeminiClient(api_key=GEMINI)

    # Generator responsável por gerar imagens + aplicar logo
    post_generator = PostGenerator(gemini_client)

    # ==========================
    # REPOSITORIES
    # ==========================
    post_repository = PostRepository()

    # ==========================
    # SERVICES EXISTENTES
    # ==========================
    usuario_service = UsuarioService()
    corrida_service = CorridaService()
    relatorio_service = RelatorioService()
    vision_service = TreinoVisionService(GEMINI)

    # ==========================
    # NOVO POST SERVICE
    # ==========================
    post_service = PostService(
        post_repository=post_repository,
        corrida_service=corrida_service,
        post_generator=post_generator
    )

    # ==========================
    # DICIONÁRIO DE SERVICES
    # ==========================
    services = {
        "usuario": usuario_service,
        "corrida": corrida_service,
        "relatorio": relatorio_service,
        "vision": vision_service,
        "post": post_service,   # 👈 NOVO SERVICE
        "log": log,
    }

    # ==========================
    # REGISTRAR TODOS HANDLERS
    # ==========================
    register_handlers(bot, services)

    log.info("Bot Telegram configurado com sucesso")

    return bot