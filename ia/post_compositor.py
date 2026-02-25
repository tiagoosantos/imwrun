from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path


class PostCompositor:

    WIDTH = 1080
    HEIGHT = 1920

    def __init__(self, logo_path: str):
        self.logo_path = logo_path

    def compor(
        self,
        foto_usuario_path: str,
        dados: dict,
        output_path: str
    ):

        # 🎨 Base preta
        base = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (0, 0, 0, 255))

        # 📷 Foto do usuário
        foto = Image.open(foto_usuario_path).convert("RGBA")

        # Ajustar proporção mantendo centro
        foto = self._resize_cover(foto, self.WIDTH, self.HEIGHT)

        # Escurecer levemente para texto ficar legível
        overlay = Image.new("RGBA", (self.WIDTH, self.HEIGHT), (0, 0, 0, 120))
        foto = Image.alpha_composite(foto, overlay)

        base = foto

        draw = ImageDraw.Draw(base)

        # 🔤 Fontes
        font_titulo = ImageFont.truetype("assets/fonts/Montserrat-Bold.ttf", 90)
        font_dados = ImageFont.truetype("assets/fonts/Montserrat-SemiBold.ttf", 70)

        # 🏃 Título
        draw.text(
            (self.WIDTH // 2, 250),
            "TREINO CONCLUÍDO",
            font=font_titulo,
            fill="white",
            anchor="mm"
        )

        # 📊 Dados do treino
        texto_dados = (
            f"{dados['distancia']} km\n"
            f"{dados['tempo']}\n"
            f"Pace {dados['pace']}\n"
            f"{dados['calorias']} kcal"
        )

        draw.multiline_text(
            (self.WIDTH // 2, 1400),
            texto_dados,
            font=font_dados,
            fill="white",
            anchor="mm",
            align="center",
            spacing=20
        )

        # 🏷 Logo
        logo = Image.open(self.logo_path).convert("RGBA")
        logo = logo.resize((220, 220), Image.LANCZOS)

        base.paste(logo, (self.WIDTH - 260, 60), logo)

        base.convert("RGB").save(output_path, quality=95)

    def _resize_cover(self, image, target_w, target_h):
        ratio = max(target_w / image.width, target_h / image.height)
        new_size = (int(image.width * ratio), int(image.height * ratio))
        image = image.resize(new_size, Image.LANCZOS)

        left = (image.width - target_w) // 2
        top = (image.height - target_h) // 2
        right = left + target_w
        bottom = top + target_h

        return image.crop((left, top, right, bottom))