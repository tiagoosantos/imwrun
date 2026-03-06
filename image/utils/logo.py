from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent.parent
TEMP_DIR = BASE_DIR / "temp" / "posts"
LOGO_PATH = BASE_DIR / "assets" / "logos" / "imwrun_logo.jpeg"

# ==========================
# LOGO CENTRAL
# ==========================

def aplicar_logo_central(img):

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
# LOGO CANTO
# ==========================

def aplicar_logo_canto(img):

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