from enum import StrEnum


class PromptTipo(StrEnum):
    PREMIUM = "premium"
    CLEAN = "clean"
    ARTISTICO = "artistico"
    CARTOON = "cartoon"


PROMPTS = {
    PromptTipo.PREMIUM: """
Transforme esta foto de corrida em uma versao esportiva premium.

Estilo:
- Visual cinematografico
- Cores vibrantes
- Alto contraste
- Atmosfera dinamica
- Sensacao de performance

Destaque os dados do treino na imagem usando o modelo strava:

- Distancia: {distancia}
- Tempo: {tempo}
- Pace: {pace}

Mantenha o atleta realista.
Nao escreva a palavra 'None' na imagem.
""",
    PromptTipo.CLEAN: """
A primeira imagem e a foto do corredor.
A segunda imagem e um logo oficial chamado "logo".

Estilo:
- Visual cinematografico
- Cores vibrantes
- Atmosfera dinamica
- Sensacao de performance

Destaque o treino na imagem usando o modelo strava apenas com os dados disponiveis:
Distancia: {distancia}
Tempo: {tempo}
Pace: {pace}

Com base nas informacoes da cena de fundo, crie uma composicao clean e visualmente impressionante que integre o logo de forma harmoniosa, sem sobrepor ou distorcer a imagem do corredor, por fim aplique um desfoque de 30%.
Mantenha o atleta realista e nao altere sua aparencia ou o corpo.
Nao escreva a palavra 'None' na imagem.

Use a imagem chamada "logo" como logotipo oficial.
Posicione o logo proximo a um dos cantos da imagem
(canto inferior direito ou superior direito),
mantendo proporcao e sem distorcer.
""",
    PromptTipo.ARTISTICO: """
Acao: Criar uma postagem de rede social vertical (9:16) com um estilo "Artistico e de Design Expresso", elevando a foto original para uma composicao de arte digital fluida.

Composicao Visual:
Sujeito: Um corredor central (masculino ou feminino, baseado na imagem original), mantendo a expressao confiante e sorridente e sinais visiveis de esforco, em pose de corrida ou pos-corrida. A identidade da imagem original e mantida apenas como base de expressao para um corredor generalizado.
Cenario de Fundo (Reimaginado): O ambiente original e completamente reimaginado como uma vasta pintura abstrata fluida, com textura rica e pinceladas visiveis, usando tons profundos, com padroes geometricos abstratos e uma sensacao de movimento que se funde com o corredor, como se o mundo todo fosse uma tela monumental.
Iluminacao e Atmosfera: As luzes ambientais originais sao transformadas em feixes de luz de estudio texturizados e coloridos, projetando sombras longas e padroes de luz complexos sobre o corredor e o solo. Uma nevoa colorida difunde a cena.

Integracao de Design:
Textura na Vestimenta: Sutilmente, sobreponha padroes topograficos e uma malha de dados translucida sobre a camiseta ou vestuario do corredor.
Formas de Dados Flutuantes: No canto inferior, apresente os dados contidos dentro de formas organicas, poligonais e translucidas que flutuam na cena. Cada forma tem uma textura e icone integrados:

[Painel 1] Icone de Cronometro + TEMPO: {tempo}
[Painel 2] Icone de Pin de Mapa + DISTANCIA: {distancia}
[Painel 3] Icone de Tenis + PACE: {pace}

Elementos de Marca e Texto:
Canto Superior Esquerdo: "[NOME_DA_MARCA/CLUBE] LOGO" integrado de forma sutil a textura do mural abstrato.
Canto Superior Direito: "[NOME_DA_SESSAO/CORRIDA]" em fonte moderna, integrado sutilmente a luz projetada.

Acabamento: O suor e realcado com micro-glitter, e o concreto ou solo do local tem linhas graficas de GPS integradas. O resultado deve parecer uma fusao de fotografia e design de arte.
""",
    PromptTipo.CARTOON: """
Geracao de imagem vertical para redes sociais (como Reels/TikTok) em estilo anime de alta qualidade.

Sujeito Principal: Uma representacao de anime detalhada e dinamica de um corredor ou corredora generico(a), em pleno movimento de corrida com passada media e bracos bombeando. O corredor veste equipamento de corrida de performance de cores vivas e um relogio de esporte moderno. Sua expressao e focada e determinada.

Cenario: Um local de corrida noturno iconico. O plano de fundo e redesenhado em estilo anime de alta qualidade e com cores aprimoradas. O piso tem marcas de passos sutis. As luzes de rua fortes estao presentes, criando feixes de luz dramaticos e lens flares coloridos e estilizados. Arvores e predios distantes sob o ceu noturno. Linhas de velocidade sutis no ar ao redor do corredor.

Overlays de Marketing:

Canto superior esquerdo: O logo "RUNNERS CLUB" com o icone de corredor.
Canto superior direito: O texto "NIGHT SESSION DONE" em fonte moderna e limpa.
Canto inferior: Uma caixa preta translucida flutuante com icones e dados de corrida variaveis:

Tempo (com cronometro): {tempo}
Distancia (com mapa): {distancia}
Pace (com tenis): {pace}

Todos os textos e icones nitidos e modernos. O tenis no overlay e um modelo de tenis de corrida de performance.

Composicao: O corredor posicionado para preencher o espaco, em direcao ao espectador ou em angulo dinamico de 3/4, overlays legiveis e sem cobrir rosto ou corpo. Iluminacao noturna dramatica criando contrastes interessantes. Apelo visual de abertura de anime ou poster de evento.
""",
}


def _normalizar_tipo(tipo: PromptTipo | str) -> PromptTipo:
    if isinstance(tipo, PromptTipo):
        return tipo

    try:
        return PromptTipo(str(tipo).strip().lower())
    except ValueError as exc:
        tipos_disponiveis = ", ".join(item.value for item in PromptTipo)
        raise ValueError(
            f"Tipo de prompt invalido: {tipo!r}. Use um destes: {tipos_disponiveis}."
        ) from exc


def _valor_campo(valor, sufixo: str = "") -> str:
    if valor is None or str(valor).strip() == "":
        return "nao informado"

    texto = str(valor).strip()
    if sufixo and texto.lower().endswith(sufixo.strip().lower()):
        return texto

    return f"{texto}{sufixo}"


def render_prompt(
    tipo: PromptTipo | str,
    distancia=None,
    tempo=None,
    pace=None,
    extra=None,
) -> str:
    template = PROMPTS[_normalizar_tipo(tipo)]

    prompt = template.format(
        distancia=_valor_campo(distancia, " km"),
        tempo=_valor_campo(tempo),
        pace=_valor_campo(pace),
    )

    if extra and extra.strip():
        prompt += f"\n\nEstilo adicional solicitado: {extra.strip()}"

    return prompt.strip()
