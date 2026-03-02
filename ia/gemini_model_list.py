# %%
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


# from google import genai

# client = genai.Client(api_key=GEMINI)

# print("Verificando modelos com suporte a GERAÇÃO DE IMAGEM...\n")

# try:
#     # Listamos todos os modelos disponíveis para sua chave
#     for m in client.models.list():
#         # Na nova SDK, verificamos se 'generate_image' está nas ações suportadas
#         if 'generate_image' in m.supported_actions:
#             print(f"✅ CONFIRMADO: {m.name}")
#             print(f"   Descrição: {m.description}\n")
#         else:
#             print(f"❌ {m.name} - NÃO SUPORTA GERAÇÃO DE IMAGEM")
            
# except Exception as e:
#     print(f"Erro ao listar modelos: {e}")