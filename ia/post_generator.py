import uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

# ==========================
# PATHS BASE
# ==========================

BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp" / "posts"
LOGO_PATH = BASE_DIR / "assets" / "logos" / "imwrun_logo.jpeg"

TEMP_DIR.mkdir(parents=True, exist_ok=True)


# ==========================
# POST GENERATOR
# ==========================

class PostGenerator:

    WIDTH = 1080
    HEIGHT = 1920

    def __init__(self):
        pass

    # ==========================
    # MÉTODO PRINCIPAL
    # ==========================

    def gerar(self, fotos: list[str], dados: dict) -> list[str]:
        """
        fotos: lista de paths das fotos enviadas pelo usuário
        dados: dict com:
            {
                "distancia": "5.00",
                "tempo": "00:25:30",
                "pace": "5:06/km",
                "calorias": "420"
            }
        """

        arquivos_salvos = []

        for variacao in range(3):  # gerar 3 variações

            output_path = TEMP_DIR / f"{uuid.uuid4()}.jpg"

            self._compor_post(
                foto_usuario_path=fotos[0],
                dados=dados,
                output_path=str(output_path),
                variacao=variacao
            )

            arquivos_salvos.append(str(output_path))

        return arquivos_salvos

    # ==========================
    # COMPOSIÇÃO PRINCIPAL
    # ==========================

    def _compor_post(self, foto_usuario_path, dados, output_path, variacao=0):

        base = Image.open(foto_usuario_path).convert("RGBA")

        # 🔹 Ajustar para 1080x1920 estilo cover
        base = self._resize_cover(base, self.WIDTH, self.HEIGHT)

        # 🔹 Escurecer fundo para legibilidade
        enhancer = ImageEnhance.Brightness(base)
        base = enhancer.enhance(0.6)

        draw = ImageDraw.Draw(base)

        # 🔹 Fontes (ajuste se necessário)
        try:
            font_titulo = ImageFont.truetype(
                str(BASE_DIR / "assets/fonts/Montserrat-Bold.ttf"),
                90
            )
        except:
            font_titulo = ImageFont.load_default()

        try:
            font_dados = ImageFont.truetype(
                str(BASE_DIR / "assets" / "fonts" / "Montserrat-SemiBold.ttf"),
                70
            )
        except:
            font_dados = ImageFont.load_default()

        # 🔹 Posição do título varia
        if variacao == 0:
            y_titulo = 250
        elif variacao == 1:
            y_titulo = 400
        else:
            y_titulo = 150

        # 🔹 Título
        draw.text(
            (self.WIDTH // 2, y_titulo),
            "TREINO CONCLUÍDO",
            font=font_titulo,
            fill="white",
            anchor="mm"
        )

        # 🔹 Dados do treino
        texto = (
            f"{dados['distancia']} km\n"
            f"{dados['tempo']}\n"
            f"Pace {dados['pace']}\n"
            f"{dados['calorias']} kcal"
        )

        draw.multiline_text(
            (self.WIDTH // 2, 1400),
            texto,
            font=font_dados,
            fill="white",
            anchor="mm",
            align="center",
            spacing=20
        )

        # 🔹 Aplicar logo
        self._aplicar_logo(base)

        base.convert("RGB").save(output_path, quality=95)

    # ==========================
    # RESIZE COVER (estilo CSS)
    # ==========================

    def _resize_cover(self, image, target_w, target_h):

        ratio = max(target_w / image.width, target_h / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.LANCZOS)

        left = (image.width - target_w) // 2
        top = (image.height - target_h) // 2
        right = left + target_w
        bottom = top + target_h

        return image.crop((left, top, right, bottom))

    # ==========================
    # APLICAR LOGO
    # ==========================

    def _aplicar_logo(self, base_image):
        print("aplicando logo")
        if not LOGO_PATH.exists():
            print(f"Logo não encontrado em: {LOGO_PATH}")
            return

        logo = Image.open(LOGO_PATH).convert("RGBA")

        # 🔹 Garantir tamanho mínimo
        largura_base = base_image.width
        logo_ratio = 0.18

        nova_largura = max(150, int(largura_base * logo_ratio))
        proporcao = nova_largura / logo.width
        nova_altura = int(logo.height * proporcao)

        logo = logo.resize((nova_largura, nova_altura), Image.LANCZOS)

        # 🔹 Criar sombra leve para destacar
        sombra = Image.new("RGBA", logo.size, (0, 0, 0, 120))

        margem = 40

        pos_x = base_image.width - logo.width - margem
        pos_y = base_image.height - logo.height - margem

        # 🔹 Aplicar sombra primeiro
        base_image.paste(sombra, (pos_x + 5, pos_y + 5), sombra)

        # 🔹 Aplicar logo
        base_image.paste(logo, (pos_x, pos_y), logo)