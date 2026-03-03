import os
import uuid
import logging
from PIL import Image
from google import genai
from google.genai import types
from config.settings import GEMINI


class GeminiImageService:
    """
    Serviço de geração de imagem via Gemini (image-to-image)
    baseado exatamente no padrão validado no teste_de_imagem2.py
    """

    def __init__(self):
        self.log = logging.getLogger(__name__)

        self.client = genai.Client(api_key=GEMINI)

        self.model = "gemini-3.1-flash-image-preview"

        self.output_dir = "temp/gemini"
        os.makedirs(self.output_dir, exist_ok=True)

    # ==========================================================
    # MÉTODO PÚBLICO
    # ==========================================================

    def gerar_imagem_estilizada(
        self,
        image_path: str,
        dados_treino: dict,
        prompt_usuario: str,
    ) -> str:

        prompt_final = self._montar_prompt(dados_treino, prompt_usuario)

        try:
            image = Image.open(image_path)

            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt_final, image],
                config=types.GenerateContentConfig(
                    image_config=types.ImageConfig(
                        aspect_ratio="16:9"
                    )
                ),
            )

            output_path = self._extrair_e_salvar(response)

            self.log.info("Imagem Gemini gerada com sucesso")

            return output_path

        except Exception:
            self.log.error("Erro ao gerar imagem via Gemini", exc_info=True)
            raise

    # ==========================================================
    # MÉTODOS INTERNOS
    # ==========================================================

    def _montar_prompt(self, dados_treino: dict, prompt_usuario: str) -> str:

        distancia = dados_treino.get("distancia")
        tempo = dados_treino.get("tempo")
        pace = dados_treino.get("pace")
        calorias = dados_treino.get("calorias")

        # Estilize esta foto de corrida com arte digital vibrante e moderna.

        prompt = f"""
        Transforme esta foto de corrida em uma versão esportiva premium.

        Estilo:
        - Visual cinematográfico
        - Cores vibrantes
        - Alto contraste
        - Atmosfera dinâmica
        - Sensação de performance

        Destaque os dados do treino na imagem usando o modelo strava:

        - Distância: {distancia} km
        - Tempo: {tempo}
        - Pace: {pace}
        - Calorias: {calorias} kcal

        Mantenha o atleta realista.
        Não escreva a palavra 'None' na imagem.
        """

        if prompt_usuario:
            prompt += f"\nEstilo adicional solicitado: {prompt_usuario}"

        return prompt.strip()

    def _extrair_e_salvar(self, response):

        for part in response.parts:

            if part.inline_data is not None:

                image = part.as_image()

                file_name = f"gemini_{uuid.uuid4().hex}.png"
                output_path = os.path.join(self.output_dir, file_name)

                image.save(output_path)

                return output_path

        raise RuntimeError("Gemini não retornou imagem válida")