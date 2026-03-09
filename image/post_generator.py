import uuid
from pathlib import Path
from PIL import Image, ImageEnhance

from image.styles import anime, cartoon, sketch, comic, comic_cv, manga_cv, sketch_cv, cartoon_cv, anime_gan
from image.layouts import layout_glass, layout_classic
from image.styles import anime_gan
from image.utils.resize import resize_cover
from image.utils.logo import aplicar_logo_central, aplicar_logo_canto

BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp" / "posts"
LOGO_PATH = BASE_DIR / "assets" / "logos" / "imwrun_logo.jpeg"


TEMP_DIR.mkdir(parents=True, exist_ok=True)


class PostGenerator:

    WIDTH = 1080
    HEIGHT = 1920

    def gerar(self, fotos: list[str], dados: dict, gemini_ativo: bool = False) -> list[str]:

        arquivos_salvos = []

        foto_base = fotos[0]

        # ==========================
        # PRIMEIRA IMAGEM (layout novo)
        # ==========================

        img1_path = TEMP_DIR / f"{uuid.uuid4()}.jpg"
        self._gerar_primeira_imagem(foto_base, dados, img1_path)
        arquivos_salvos.append(str(img1_path))

        # ==========================
        # ESTILOS LOCAIS
        # ==========================

        estilos = {
            # "anime": anime.aplicar,
            # "sketch": sketch.aplicar,
            # "comic": comic.aplicar,
            # "cartoon_cv": cartoon_cv.aplicar,
            # "comic_cv": comic_cv.aplicar,
            # "manga_cv": manga_cv.aplicar,
            # "sketch_cv": sketch_cv.aplicar,
            # "anime_gan": anime_gan.aplicar
        }
        
        for nome, func in estilos.items() or []:

            path = TEMP_DIR / f"{uuid.uuid4()}_{nome}.jpg"

            self._gerar_estilo(foto_base, dados, path, func)

            arquivos_salvos.append(str(path))

        return arquivos_salvos

    # ==========================
    # PRIMEIRA IMAGEM (NOVA)
    # ==========================

    def _gerar_primeira_imagem(self, foto_usuario_path, dados, output_path):

        base = Image.open(foto_usuario_path).convert("RGBA")

        base = resize_cover(base, self.WIDTH, self.HEIGHT)

        contraste = ImageEnhance.Contrast(base)
        base = contraste.enhance(1.25)

        cor = ImageEnhance.Color(base)
        base = cor.enhance(1.2)

        layout_glass.aplicar_layout_glass(base, dados)
        # layout_glass.aplicar_layout_glass_acima_logo(base, dados)
        # layout_glass.aplicar_layout_glass_footer(base, dados)

        aplicar_logo_central(base)

        base.convert("RGB").save(output_path, quality=95)

    # ==========================
    # GERAR ESTILOS
    # ==========================

    def _gerar_estilo(self, foto_usuario_path, dados, output_path, estilo_func):

        base = Image.open(foto_usuario_path).convert("RGBA")

        base = resize_cover(base, self.WIDTH, self.HEIGHT)

        base = estilo_func(base)

        contraste = ImageEnhance.Contrast(base)
        base = contraste.enhance(1.25)

        cor = ImageEnhance.Color(base)
        base = cor.enhance(1.2)

        layout_classic.aplicar_layout_classic(base, dados)

        aplicar_logo_canto(base)

        base.convert("RGB").save(output_path, quality=95)
