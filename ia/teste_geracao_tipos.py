import argparse
import logging
from datetime import datetime
from pathlib import Path

from ia.gemini_image_service import GENERATED_DIR, GeminiImageService
from ia.gemini_prompt import PromptTipo


# Preencha estes valores quando quiser rodar o teste direto pelo arquivo.
FOTO_TESTE = r"C:\Users\x002426\Downloads\diogo.jpg"
DISTANCIA_TESTE = "5,00 km"
TEMPO_TESTE = "25:00"
PACE_TESTE = "05:00/km"
EXTRA_TESTE = None
TELEGRAM_ID_TESTE = 999999
TEST_OUTPUT_DIR = GENERATED_DIR / "teste"
TEST_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Gera imagens por IA para todos os estilos disponiveis."
    )
    parser.add_argument(
        "foto",
        nargs="?",
        help="Caminho da foto base que sera enviada ao Gemini.",
    )
    parser.add_argument(
        "--distancia",
        default="5,00 km",
        help="Distancia do treino exibida no prompt.",
    )
    parser.add_argument(
        "--tempo",
        default="25:00",
        help="Tempo do treino exibido no prompt.",
    )
    parser.add_argument(
        "--pace",
        default="05:00/km",
        help="Pace do treino exibido no prompt.",
    )
    parser.add_argument(
        "--extra",
        default=None,
        help="Instrucao extra adicionada ao prompt.",
    )
    parser.add_argument(
        "--telegram-id",
        type=int,
        default=999999,
        help="Identificador usado apenas para nomear os arquivos gerados.",
    )
    return parser.parse_args()


def renomear_saida(caminho_original: str, prompt_tipo: PromptTipo) -> Path:
    origem = Path(caminho_original)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    destino = TEST_OUTPUT_DIR / f"teste_{prompt_tipo.value}_{timestamp}{origem.suffix}"
    origem.replace(destino)
    return destino


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    args = parse_args()
    foto_informada = args.foto or FOTO_TESTE

    if not foto_informada:
        raise ValueError(
            "Informe a foto no argumento ou preencha FOTO_TESTE no arquivo."
        )

    foto = Path(foto_informada).expanduser().resolve()

    if not foto.exists():
        raise FileNotFoundError(f"Foto nao encontrada: {foto}")

    service = GeminiImageService()
    dados_treino = {
        "distancia": args.distancia if args.distancia != "5,00 km" else DISTANCIA_TESTE,
        "tempo": args.tempo if args.tempo != "25:00" else TEMPO_TESTE,
        "pace": args.pace if args.pace != "05:00/km" else PACE_TESTE,
    }
    extra = args.extra if args.extra is not None else EXTRA_TESTE
    telegram_id = (
        args.telegram_id if args.telegram_id != 999999 else TELEGRAM_ID_TESTE
    )
    resultados = []

    print(f"Foto base: {foto}")
    print(f"Saida: {TEST_OUTPUT_DIR}")
    print("")

    for prompt_tipo in PromptTipo:
        print(f"[INICIO] Gerando estilo: {prompt_tipo.value}")

        caminho_gerado = service.gerar_imagem_estilizada(
            telegram_id=telegram_id,
            image_path=str(foto),
            dados_treino=dados_treino,
            prompt_tipo=prompt_tipo,
            prompt_usuario=extra,
        )

        caminho_final = renomear_saida(caminho_gerado, prompt_tipo)
        resultados.append((prompt_tipo.value, caminho_final))

        print(f"[OK] {prompt_tipo.value}: {caminho_final}")
        print("")

    print("Resumo final:")
    for estilo, caminho in resultados:
        print(f"- {estilo}: {caminho}")


if __name__ == "__main__":
    main()
