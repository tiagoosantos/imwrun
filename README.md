# 🏃‍♂️ Corrida Bot

Bot de Telegram para registro e acompanhamento de corridas, com cálculo
de pace, rankings e estatísticas mensais.

Projeto desenvolvido com arquitetura em camadas (Telegram → Service →
Repository → PostgreSQL), seguindo boas práticas de separação de
responsabilidades.

------------------------------------------------------------------------

# 🚀 Funcionalidades

-   Registro de corrida passo a passo\
-   Cálculo automático de pace\
-   Possibilidade de informar pace manual\
-   Ranking por quilometragem\
-   Ranking por tempo total\
-   Estatísticas mensais\
-   Validação robusta de entrada\
-   Cancelamento com `sair` em qualquer etapa\
-   Wrapper resiliente com auto-restart\
-   Logs estruturados

------------------------------------------------------------------------

# 🧱 Arquitetura

    Telegram (Interface)
            ↓
    CorridaService (Regras de negócio)
            ↓
    CorridaRepository (Persistência)
            ↓
    PostgreSQL (Banco de dados)

Separação clara:

-   Interface → apenas interação\
-   Service → regras e cálculos\
-   Repository → SQL puro\
-   Banco → armazenamento consistente (inteiros)

------------------------------------------------------------------------

# 🗄 Modelagem do Banco

Todas as métricas são armazenadas como **inteiros**, evitando problemas
com float.

## 📌 Tabela `usuarios`

-   telegram_id BIGINT PRIMARY KEY\
-   nome VARCHAR(100)\
-   criado_em TIMESTAMP

## 📌 Tabela `corridas`

-   id SERIAL PRIMARY KEY\
-   telegram_id BIGINT\
-   tempo_segundos INTEGER\
-   distancia_metros INTEGER\
-   pace_segundos INTEGER\
-   pace_origem VARCHAR(20)\
-   passos INTEGER\
-   calorias INTEGER\
-   data_corrida TIMESTAMP

------------------------------------------------------------------------

# 📊 Rankings

### Ranking por KM

Ordenado por soma de distância.

### Ranking por Tempo

Ordenado por soma de tempo total em segundos.

------------------------------------------------------------------------

# 🧠 Regras de Negócio

-   Se o usuário informar pace manual → sistema valida e usa\
-   Se informar `0` → pace é calculado automaticamente\
-   Distância aceita múltiplos formatos:
    -   `5`
    -   `5.2`
    -   `5,250`
    -   `5250`
-   Tempo aceita:
    -   `MM:SS`
    -   `MM.SS`
    -   com ou sem espaços\
-   Em qualquer etapa, digitar `sair` cancela a operação

------------------------------------------------------------------------

# 📦 Estrutura do Projeto

    corrida_bot/
    │
    ├── main.py
    ├── wrapper.py
    ├── telegram.py
    ├── corrida_service.py
    ├── repository/
    │   └── corrida_repository.py
    ├── database/
    │   └── connection.py
    ├── utils/
    │   ├── parse_utils.py
    │   └── format_utils.py

------------------------------------------------------------------------

# ⚙️ Instalação

## 1️⃣ Clonar repositório

    git clone https://github.com/seu-usuario/corrida-bot.git
    cd corrida-bot

## 2️⃣ Criar ambiente virtual

    python -m venv venv
    source venv/bin/activate  # Linux
    venv\Scripts\activate     # Windows

## 3️⃣ Instalar dependências

    pip install -r requirements.txt

Principais libs:

-   pyTelegramBotAPI\
-   psycopg2\
-   python-dotenv

------------------------------------------------------------------------

# 🔐 Variáveis de Ambiente

Crie um `.env`:

    TELEGRAM_TOKEN=seu_token_aqui
    DB_HOST=localhost
    DB_NAME=corrida
    DB_USER=postgres
    DB_PASSWORD=senha

------------------------------------------------------------------------

# ▶️ Executar

    python main.py

O wrapper mantém o bot ativo mesmo em caso de erro.

------------------------------------------------------------------------

# 📈 Exemplo de Exibição

    🏃 Corrida #12
    ⏱ Tempo: 45:30
    📏 Distância: 5,25 km
    🔥 Pace: 08:40/km

------------------------------------------------------------------------

# 🛡 Boas Práticas Aplicadas

-   Sem uso de float para métricas\
-   Separação clara de camadas\
-   Logs estruturados\
-   Tratamento de exceções\
-   Retry automático no wrapper\
-   SQL parametrizado (evita SQL Injection)

------------------------------------------------------------------------

# 🔮 Melhorias Futuras

-   Ranking por melhor pace\
-   Comparação de evolução\
-   Estatísticas semanais\
-   Exportação para Excel\
-   Dashboard web\
-   API REST\
-   Testes automatizados

------------------------------------------------------------------------

# 📄 Licença

MIT

------------------------------------------------------------------------

# 👨‍💻 Autor

Tiago Oliveira Santos
