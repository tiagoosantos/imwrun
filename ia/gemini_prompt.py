prompt2 = f"""
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

Mantenha o atleta realista.
Não escreva a palavra 'None' na imagem.
"""

prompt1 = f"""
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

# PROMPT ARTISTICO
PROMPT4 = f"""
Ação: Criar uma postagem de rede social vertical (9:16) com um estilo "Artístico e de Design Expresso", elevando a foto original para uma composição de arte digital fluida.

Composição Visual:
Sujeito: Um central central (masculino ou feminino, o [CORREDOR_GÊNERO] de image_0.png), mantendo a expressão confiante e sorridente e sinais visíveis de esforço (suor, rosto corado), em pose de corrida ou pós-corrida. A identidade de image_0.png é mantida apenas como base de expressão para um corredor generalizado.
Cenário de Fundo (Reimaginado): O ambiente original é completamente reimaginado como uma vasta pintura abstrata fluida, com textura rica e pinceladas visíveis, usando tons profundos (ex: azuis intensos e laranjas queimados), com padrões geométricos abstratos e uma sensação de movimento que se funde com o corredor, como se o mundo todo fosse uma tela monumental.
Iluminação e Atmosfera: As luzes ambientais originais são transformadas em feixes de luz de estúdio texturizados e coloridos (por exemplo, azul-petróleo frio e ocre quente), projetando sombras longas e padrões de luz complexos sobre o corredor e o solo. Uma névoa colorida difunde a cena.

Integração de Design: Textura na Vestimenta: Sutilmente, sobreponha padrões topográficos e uma malha de dados translúcida sobre a camiseta/vestuário do corredor.
Formas de Dados Flutuantes: No canto inferior, apresente os dados contidos dentro de formas orgânicas, poligonais e translúcidas (idênticas às de image_8.png) que flutuam na cena. Cada forma tem uma textura e ícone integrados:

[Painel 1] Ícone de Cronômetro + TEMPO: [{tempo}]
[Painel 2] Ícone de Pin de Mapa + DISTÂNCIA: [{distancia}]
[Painel 3] Ícone de Tênis + PACE: [{pace}]

Elementos de Marca e Texto:
Canto Superior Esquerdo: "[NOME_DA_MARCA/CLUBE] LOGO" (menor e integrado de forma mais sutil à textura do mural abstrato).
Canto Superior Direito: "[NOME_DA_SESSÃO/CORRIDA]" (em fonte moderna, integrado sutilmente à luz projetada).

Acabamento: O suor é realçado com micro-glitter, e o concreto/solo do local tem linhas gráficas de GPS integradas. O resultado deve parecer uma fusão de fotografia e design de arte.
"""

# PROMPT CARTOON
PROMPT5 = f"""
Geração de imagem vertical para redes sociais (como Reels/TikTok) em estilo anime de alta qualidade.

Sujeito Principal: Uma representação de anime detalhada e dinâmica de um corredor ou corredora genérico(a) (etnia e gênero variáveis, mas com aparência atlética e em forma), em pleno movimento de corrida com passada média e braços bombeando. O corredor veste equipamento de corrida de performance de cores vivas e um relógio de esporte moderno. Sua expressão é focada e determinada.

Cenário: Um local de corrida noturno icônico (como uma ciclovia de cidade costeira, uma trilha de parque iluminada, ou ruas de metrópole ao anoitecer). O plano de fundo é redesenhado em estilo anime de alta qualidade e com cores aprimoradas. Em vez do mural de basquete, a parede de concreto limpa tem sutil arte urbana abstrata genérica ou arte de desempenho em tons mais vibrantes e traços nítidos. O piso (concreto ou trilha) tem marcas de passos sutis. As luzes de rua fortes estão presentes, criando feixes de luz dramáticos e lens flares coloridos e estilizados. Árvores e prédios distantes sob o céu noturno. Linhas de velocidade sutis no ar ao redor do corredor.

Overlays de Marketing (Posições Mantidas, Conteúdo Generalizado/Variável):

Canto superior esquerdo: O logo "RUNNERS CLUB" com o ícone de corredor (mantido).

Canto superior direito: O texto "NIGHT SESSION DONE" em fonte moderna e limpa (mantido).

Canto inferior: Uma caixa preta translúcida flutuante com ícones e dados de corrida variáveis (com ícones: cronômetro, mapa, tênis):

Tempo (com cronômetro): {tempo}

Distância (com mapa): {distancia}

Pace (com tênis): {pace}

Todos os textos e ícones nítidos e modernos. O tênis no overlay é um modelo de tênis de corrida de performance.

Composição: O corredor posicionado para preencher o espaço, em direção ao espectador ou ângulo dinâmico de 3/4, overlays legíveis e sem cobrir rosto/corpo. Iluminação noturna dramática criando contrastes interessantes. Apelo visual de abertura de anime ou pôster de evento.
"""