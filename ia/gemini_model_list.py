from google import genai
from config.settings import GEMINI  # usa sua API key já configurada


def listar_modelos():
    client = genai.Client(api_key=GEMINI)

    print("\n🔎 Modelos disponíveis para sua API key:\n")

    try:
        for model in client.models.list():
            print(f"• {model.name}")
    except Exception as e:
        print("❌ Erro ao listar modelos:")
        print(e)


if __name__ == "__main__":
    listar_modelos()