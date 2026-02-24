import base64
import uuid
from pathlib import Path
from PIL import Image


# ==========================
# PATHS BASE
# ==========================

BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp" / "posts"
LOGO_PATH = BASE_DIR / "assets" / "logos" / "imwrun_logo.png"

TEMP_DIR.mkdir(parents=True, exist_ok=True)


# ==========================
# POST GENERATOR
# ==========================

class PostGenerator:

    def __init__(self, gemini_client):
        """
        gemini_client deve ter um método:
        generate_images(prompt: str, images: list[str], n: int) -> list[bytes]
        """
        self.gemini = gemini_client

    # ==========================
    # MÉTODO PRINCIPAL
    # ==========================

    def gerar(self, fotos: list[str], prompt: str) -> list[str]:

        # 1️⃣ Converter imagens para base64
        imagens_base64 = [self._encode_image(p) for p in fotos]

        # 2️⃣ Solicitar 3 imagens ao Gemini
        imagens_geradas_bytes = self.gemini.generate_images(
            prompt=prompt,
            images=imagens_base64,
            n=3,
            size="1080x1920"
        )

        # 3️⃣ Salvar + aplicar logo
        arquivos_salvos = []

        for img_bytes in imagens_geradas_bytes:

            path = self._salvar_imagem(img_bytes)

            self._aplicar_logo(path)

            arquivos_salvos.append(path)

        return arquivos_salvos

    # ==========================
    # ENCODE BASE64
    # ==========================

    def _encode_image(self, path: str) -> str:

        with open(path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")

    # ==========================
    # SALVAR IMAGEM
    # ==========================

    def _salvar_imagem(self, image_bytes: bytes) -> str:

        filename = f"{uuid.uuid4()}.png"
        path = TEMP_DIR / filename

        with open(path, "wb") as f:
            f.write(image_bytes)

        return str(path)

    # ==========================
    # APLICAR LOGO
    # ==========================

    def _aplicar_logo(self, image_path: str):

        if not LOGO_PATH.exists():
            return  # evita erro se logo não existir

        base = Image.open(image_path).convert("RGBA")
        logo = Image.open(LOGO_PATH).convert("RGBA")

        # 🔹 Redimensionar logo proporcionalmente
        largura_base = base.width
        logo_ratio = 0.18  # 18% da largura da imagem

        nova_largura = int(largura_base * logo_ratio)
        proporcao = nova_largura / logo.width
        nova_altura = int(logo.height * proporcao)

        logo = logo.resize((nova_largura, nova_altura), Image.LANCZOS)

        # 🔹 Posicionar no canto inferior direito
        margem = 40
        posicao = (
            base.width - logo.width - margem,
            base.height - logo.height - margem
        )

        base.paste(logo, posicao, logo)

        base.save(image_path)