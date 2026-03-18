import logging
from datetime import datetime
from pathlib import Path

from PIL import Image
from google import genai
from google.genai import types

from config.settings import GEMINI
from ia import gemini_prompt as gp


BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "logos" / "imwrun_logo.jpeg"
GENERATED_DIR = BASE_DIR / "generated_images"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)


class GeminiImageService:
    def __init__(self):
        self.log = logging.getLogger(__name__)
        self.client = genai.Client(api_key=GEMINI)
        self.model = "gemini-3.1-flash-image-preview"
        # self.model = "gemini-2.5-flash-image"

    def gerar_imagem_estilizada(
        self,
        telegram_id: int,
        image_path: str,
        dados_treino: dict | None,
        prompt_tipo: gp.PromptTipo | str = gp.PromptTipo.ARTISTICO,
        prompt_usuario: str | None = None,
    ) -> str:
        prompt_final = self._montar_prompt(
            dados_treino=dados_treino or {},
            prompt_tipo=prompt_tipo,
            prompt_usuario=prompt_usuario,
        )

        try:
            with Image.open(image_path) as image, Image.open(LOGO_PATH) as logo:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=[prompt_final, image, logo],
                    config=types.GenerateContentConfig(
                        image_config=types.ImageConfig(aspect_ratio="9:16")
                    ),
                )

            output_path = self._extrair_e_salvar(response, telegram_id)

            self.log.info(
                "Imagem Gemini gerada com sucesso",
                extra={"telegram_id": telegram_id, "prompt_tipo": prompt_tipo},
            )
            return str(output_path)

        except Exception:
            self.log.error(
                "Erro ao gerar imagem via Gemini",
                exc_info=True,
                extra={"telegram_id": telegram_id, "prompt_tipo": prompt_tipo},
            )
            raise

    def _montar_prompt(
        self,
        dados_treino: dict,
        prompt_tipo: gp.PromptTipo | str,
        prompt_usuario: str | None,
    ) -> str:
        return gp.render_prompt(
            tipo=prompt_tipo,
            distancia=dados_treino.get("distancia"),
            tempo=dados_treino.get("tempo"),
            pace=dados_treino.get("pace"),
            extra=prompt_usuario,
        )

    def _extrair_e_salvar(self, response, telegram_id: int) -> Path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        for part in getattr(response, "parts", []) or []:
            if getattr(part, "inline_data", None) is None:
                continue

            image = part.as_image()
            output_path = GENERATED_DIR / f"{telegram_id}_{timestamp}.jpg"
            image.save(output_path, format="JPEG")
            return output_path

        raise RuntimeError("Gemini nao retornou imagem valida")
