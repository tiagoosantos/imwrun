from google import genai
from PIL import Image
from config.settings import GEMINI
import io

# 1. Configuração do Cliente
client = genai.Client(api_key=GEMINI)

def estilizar_com_nano_banana(caminho_input, caminho_output, prompt_estilo):
    img = Image.open(caminho_input)
    print(f"🎨 Estilizando com Nano Banana (Gemini 3.1 Flash)...")
    
    try:
        # Seguindo a documentação: usamos generate_content com o modelo de imagem
        response = client.models.generate_content(
            model="gemini-3.1-flash-image-preview",
            contents=[
                prompt_estilo,
                img
            ]
        )

        # O segredo está em como ler a resposta
        for part in response.parts:
            if part.inline_data:
                # O método as_image() converte os bytes diretamente para um objeto PIL
                nova_img = part.as_image()
                nova_img.save(caminho_output)
                print(f"✅ SUCESSO! Imagem estilizada salva em: {caminho_output}")
                return
            elif part.text:
                print(f"Resposta em texto da IA: {part.text}")

        print("⚠️ A IA processou, mas não incluiu uma nova imagem na resposta.")

    except Exception as e:
        print(f"❌ Erro na API: {e}")

# Teste prático
estilizar_com_nano_banana(
    r"C:\Users\x002426\Downloads\20260113_061742.jpg",
    r"C:\Users\x002426\Downloads\corredor_estilizado.png",
    "Turn this photo into a professional 3D Pixar-style animation character, keeping the same running pose and clothing colors."
)