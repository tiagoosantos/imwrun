from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

BASE_DIR = Path(__file__).resolve().parent.parent.parent
print(f"BASE_DIR: {BASE_DIR}")

def aplicar_layout_glass(img, dados):

    largura, altura = img.size

    x1 = int(largura * 0.04)
    x2 = int(largura * 0.96)

    y1 = int(altura * 0.035)
    y2 = y1 + int(altura * 0.11)

    area = img.crop((x1, y1, x2, y2))
    area_blur = area.filter(ImageFilter.GaussianBlur(30))
    img.paste(area_blur, (x1, y1))

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

    try:
        font_label = ImageFont.truetype(
            str(BASE_DIR / "assets"/"fonts"/"Montserrat-Bold.ttf"), 26
        )

        font_value = ImageFont.truetype(
            str(BASE_DIR / "assets"/"fonts"/"Montserrat-SemiBold.ttf"), 56
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

        pos_label = y1 + altura_card * 0.18
        pos_value = y1 + altura_card * 0.48

        bbox_label = draw.textbbox((0, 0), labels[i], font=font_label)
        w_label = bbox_label[2] - bbox_label[0]

        draw.text(
            (centro_coluna - w_label / 2, pos_label),
            labels[i],
            fill=(210, 210, 210),
            font=font_label
        )

        bbox_value = draw.textbbox((0, 0), values[i], font=font_value)
        w_value = bbox_value[2] - bbox_value[0]

        draw.text(
            (centro_coluna - w_value / 2, pos_value),
            values[i],
            fill=(255, 255, 255),
            font=font_value
        )