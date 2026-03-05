import uuid
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp" / "posts"
LOGO_PATH = BASE_DIR / "assets" / "logos" / "imwrun_logo.jpeg"

TEMP_DIR.mkdir(parents=True, exist_ok=True)


class PostGenerator:

    WIDTH = 1080
    HEIGHT = 1920

    def gerar(self, fotos: list[str], dados: dict, quantidade: int = 2) -> list[str]:

        arquivos_salvos = []

        # PRIMEIRA IMAGEM (layout novo)
        img1_path = TEMP_DIR / f"{uuid.uuid4()}.jpg"
        self._gerar_primeira_imagem(fotos[0], dados, img1_path)
        arquivos_salvos.append(str(img1_path))

        # SEGUNDA IMAGEM (layout antigo)
        img2_path = TEMP_DIR / f"{uuid.uuid4()}.jpg"
        self._gerar_segunda_imagem(fotos[0], dados, img2_path)
        arquivos_salvos.append(str(img2_path))

        return arquivos_salvos


    # ==========================
    # PRIMEIRA IMAGEM (NOVA)
    # ==========================

    def _gerar_primeira_imagem(self, foto_usuario_path, dados, output_path):

        base = Image.open(foto_usuario_path).convert("RGBA")

        base = self._resize_cover(base, self.WIDTH, self.HEIGHT)

        contraste = ImageEnhance.Contrast(base)
        base = contraste.enhance(1.25)

        cor = ImageEnhance.Color(base)
        base = cor.enhance(1.2)

        self._desenhar_box_dados_glass(base, dados)

        self._aplicar_logo_central(base)

        base.convert("RGB").save(output_path, quality=95)


    # ==========================
    # SEGUNDA IMAGEM (ANTIGA)
    # ==========================

    def _gerar_segunda_imagem(self, foto_usuario_path, dados, output_path):

        base = Image.open(foto_usuario_path).convert("RGBA")

        base = self._resize_cover(base, self.WIDTH, self.HEIGHT)

        contraste = ImageEnhance.Contrast(base)
        base = contraste.enhance(1.25)

        cor = ImageEnhance.Color(base)
        base = cor.enhance(1.2)

        self._desenhar_box_antigo(base, dados)

        self._aplicar_logo_canto(base)

        base.convert("RGB").save(output_path, quality=95)


    # ==========================
    # NOVO CARD (GLASS)
    # ==========================

    def _desenhar_box_dados_glass(self, img, dados):

        largura, altura = img.size

        # posição do card
        x1 = int(largura * 0.04)
        x2 = int(largura * 0.96)

        y1 = int(altura * 0.035)
        y2 = y1 + int(altura * 0.11)

        # blur fundo
        area = img.crop((x1, y1, x2, y2))
        area_blur = area.filter(ImageFilter.GaussianBlur(30))
        img.paste(area_blur, (x1, y1))

        # overlay glass
        overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        draw_overlay = ImageDraw.Draw(overlay)

        draw_overlay.rounded_rectangle(
            (x1, y1, x2, y2),
            radius=50,
            fill=(0, 0, 0, 130),
            outline=(255, 255, 255, 180),
            width=3
        )

        img.alpha_composite(overlay)

        draw = ImageDraw.Draw(img)

        # fontes
        try:
            font_label = ImageFont.truetype(
                str(BASE_DIR / "assets/fonts/Montserrat-Bold.ttf"), 26
            )

            font_value = ImageFont.truetype(
                str(BASE_DIR / "assets/fonts/Montserrat-SemiBold.ttf"), 56
            )

        except:
            font_label = ImageFont.load_default()
            font_value = ImageFont.load_default()

        labels = ["Distância", "Tempo", "Pace"]

        values = [
            dados["distancia"],
            dados["tempo"],
            dados["pace"]
        ]

        largura_coluna = (x2 - x1) / 3
        altura_card = y2 - y1

        for i in range(3):

            centro_coluna = x1 + largura_coluna * i + largura_coluna / 2

            # posição vertical proporcional
            pos_label = y1 + altura_card * 0.18
            pos_value = y1 + altura_card * 0.48

            # label
            bbox_label = draw.textbbox((0, 0), labels[i], font=font_label)
            w_label = bbox_label[2] - bbox_label[0]

            draw.text(
                (centro_coluna - w_label / 2, pos_label),
                labels[i],
                fill=(210, 210, 210),
                font=font_label
            )

            # valor
            bbox_value = draw.textbbox((0, 0), values[i], font=font_value)
            w_value = bbox_value[2] - bbox_value[0]

            draw.text(
                (centro_coluna - w_value / 2, pos_value),
                values[i],
                fill=(255, 255, 255),
                font=font_value
            )


    # ==========================
    # LAYOUT ANTIGO
    # ==========================

    def _desenhar_box_antigo(self, img, dados):

        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype(
                str(BASE_DIR / "assets/fonts/Montserrat-SemiBold.ttf"),
                52
            )
        except:
            font = ImageFont.load_default()

        x = 80
        y = 120

        linhas = [
            f"Distância: {dados['distancia']}",
            f"Tempo: {dados['tempo']}",
            f"Pace: {dados['pace']}"
        ]

        for linha in linhas:

            draw.text(
                (x, y),
                linha,
                fill=(255,255,255),
                font=font
            )

            y += 80


    # ==========================
    # RESIZE COVER
    # ==========================

    def _resize_cover(self, image, target_w, target_h):

        ratio = max(target_w / image.width, target_h / image.height)

        new_size = (
            int(image.width * ratio),
            int(image.height * ratio)
        )

        image = image.resize(new_size, Image.LANCZOS)

        left = (image.width - target_w) // 2
        top = (image.height - target_h) // 2

        right = left + target_w
        bottom = top + target_h

        return image.crop((left, top, right, bottom))


    # ==========================
    # LOGO CENTRAL (NOVA IMAGEM)
    # ==========================

    def _aplicar_logo_central(self, img):

        if not LOGO_PATH.exists():
            return

        logo = Image.open(LOGO_PATH).convert("RGBA")

        largura = int(img.width * 0.32)

        proporcao = largura / logo.width
        altura = int(logo.height * proporcao)

        logo = logo.resize((largura, altura), Image.LANCZOS)

        x = (img.width - logo.width) // 2
        y = img.height - logo.height - int(img.height * 0.05)

        img.paste(logo, (x, y), logo)


    # ==========================
    # LOGO CANTO (IMAGEM ANTIGA)
    # ==========================

    def _aplicar_logo_canto(self, img):

        if not LOGO_PATH.exists():
            return

        logo = Image.open(LOGO_PATH).convert("RGBA")

        largura = int(img.width * 0.18)

        proporcao = largura / logo.width
        altura = int(logo.height * proporcao)

        logo = logo.resize((largura, altura), Image.LANCZOS)

        x = img.width - logo.width - 40
        y = img.height - logo.height - 40

        img.paste(logo, (x, y), logo)