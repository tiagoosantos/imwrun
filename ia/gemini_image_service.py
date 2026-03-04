import os
import uuid
import logging
from PIL import Image
from google import genai
from google.genai import types
from config.settings import GEMINI

from datetime import datetime
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "assets" / "logos" / "imwrun_logo.jpeg"
GENERATED_DIR = BASE_DIR / "generated_images"
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

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
        telegram_id: int,
        image_path: str,
        dados_treino: dict,
        prompt_usuario: str,
    ) -> str:

        prompt_final = self._montar_prompt(dados_treino, prompt_usuario)

        try:
            image = Image.open(image_path)
            logo = Image.open(LOGO_PATH)

            response = self.client.models.generate_content(
                model=self.model,
                contents=[prompt_final, image, logo],
                config=types.GenerateContentConfig(
                    image_config=types.ImageConfig(
                        aspect_ratio="9:16"
                    )
                ),
            )

            # output_path = self._extrair_e_salvar(response)
            output_path = self._extrair_e_salvar(response, telegram_id)

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

        prompt1 = f"""
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

        prompt = f"""
        A primeira imagem é a foto do corredor.
        A segunda imagem é um logo oficial chamado "logo".

        Estilo:
        - Visual cinematográfico
        - Cores vibrantes
        - Atmosfera dinâmica
        - Sensação de performance

        Destaque o treino na imagem usando o modelo strava apenas com os dados disponíveis:
        Distância: {distancia} km
        Tempo: {tempo}
        Pace: {pace}

        Com base nas informações da cena de fundo, crie uma composição clean e visualmente impressionante que integre o logo de forma harmoniosa, sem sobrepor ou distorcer a imagem do corredor, por fim aplique um desfoque de 30%.
        Mantenha o atleta realista e não altere sua aparência ou o corpo.
        Não escreva a palavra 'None' na imagem.

        Use a imagem chamada "logo" como logotipo oficial.
        Posicione o logo próximo a um dos cantos da imagem
        (canto inferior direito ou superior direito),
        mantendo proporção e sem distorcer.
        """ 
        #Aplique um olhar um pouco futurístico e um desfoque artístico no fundo para destacar o corredor.       

        if prompt_usuario:
            prompt += f"\nEstilo adicional solicitado: {prompt_usuario}"

        return prompt.strip()

    def _extrair_e_salvar(self, response, telegram_id):

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        for part in response.parts:

            if part.inline_data is not None:

                image = part.as_image()

                # file_name = f"gemini_{uuid.uuid4().hex}.png"
                # output_path = os.path.join(self.output_dir, file_name)

                filename = f"{telegram_id}_{timestamp}.jpg"
                output_path = GENERATED_DIR / filename

                image.save(output_path)

                return output_path

        raise RuntimeError("Gemini não retornou imagem válida")