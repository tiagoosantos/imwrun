from pathlib import Path
from PIL import ImageDraw, ImageFont

BASE_DIR = Path(__file__).resolve().parent.parent

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
            fill=(255, 255, 255),
            font=font
        )

        y += 80