import json
import mimetypes
from google import genai
from google.genai import types


class TreinoVisionService:

    def __init__(self, api_key: str):
        self.client = genai.Client(api_key=api_key)

    def analisar_imagem(self, caminho_imagem: str) -> dict:

        try:
            mime_type, _ = mimetypes.guess_type(caminho_imagem)
            if not mime_type:
                mime_type = "image/jpeg"

            prompt = """
            Analise a imagem.

            Se for um print ou foto de aplicativo de corrida
            contendo dados como distância, tempo ou pace,
            retorne:

            {
                "eh_treino": true,
                "distancia_km": float,
                "tempo": "HH:MM:SS",
                "pace": "MM:SS",
                "data": null,
                "tipo": "corrida"
            }

            Se o tempo estiver como:
            - "23min 44s"
            - "23m 44s"
            - "23:44"

            Converta para HH:MM:SS (ex: 00:23:44).

            Se NÃO for treino, retorne:
            { "eh_treino": false }

            Retorne apenas JSON válido.
            """

            with open(caminho_imagem, "rb") as img:
                image_bytes = img.read()

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    prompt,
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type,
                    ),
                ],
                config=types.GenerateContentConfig(
                    temperature=0.1,
                    response_mime_type="application/json",
                ),
            )

            texto = response.text.strip()

            print("DEBUG GEMINI:", texto)

            dados = json.loads(texto)

            if not dados.get("eh_treino"):
                return {"eh_treino": False}

            campos = ["distancia_km", "tempo", "pace", "data", "tipo"]
            for campo in campos:
                if campo not in dados:
                    dados[campo] = None

            return dados

        except Exception as e:
            print("ERRO REAL:", str(e))
            return {
                "erro": True,
                "mensagem": str(e)
            }
        
