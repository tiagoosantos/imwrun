from google import genai
from google.genai import types
from PIL import Image
import os
from config.settings import GEMINI

client = genai.Client(api_key=GEMINI)

prompt = (
    "crie uma imagem comigo correndo na pista de corrida do parque ibirapuera, em um estilo de arte digital vibrante e moderno, com cores vivas e detalhes realistas, destacando a energia e o movimento da corrida",
)

image = Image.open(r"C:\Users\x002426\Downloads\20260113_061742.jpg",)

response = client.models.generate_content(
    model="gemini-3.1-flash-image-preview",
    # model="gemini-2.5-flash-image",
    contents=[prompt, image],
    config=types.GenerateContentConfig(
        image_config=types.ImageConfig(aspect_ratio="16:9") # Opções: "1:1", "16:9", "9:16", etc.
    )
)

for part in response.parts:
    if part.text is not None:
        print(part.text)
    elif part.inline_data is not None:
        image = part.as_image()
        # se já existir um arquivo com esse nome, acrescente um número para evitar sobrescrever
        base_name = "generated_image"
        counter = 1
        filename = fr"generated_images/{base_name}.png"
        while os.path.exists(filename):
            filename = fr"generated_images/{base_name}_{counter}.png"
            counter += 1
        image.save(filename)
        print(f"Imagem salva como: {filename}")