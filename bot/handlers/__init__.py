from .start_handler import register_start
from .registro_handler import register_registro
from .pace_handler import register_pace
from .ranking_handler import register_ranking
from .relatorio_handler import register_relatorio
from .cadastro_handler import register_cadastro
from .ia_handler import register_ia

def register_handlers(bot, services):
    register_start(bot, services)
    register_registro(bot, services)
    register_pace(bot, services)
    register_ranking(bot, services)
    register_relatorio(bot, services)
    register_cadastro(bot, services)
    register_ia(bot, services)
