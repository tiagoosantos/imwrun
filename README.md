# IMW Runner Bot

Bot de Telegram para registro de treinos, leitura de imagens de aplicativos de corrida, calculo de pace, rankings, relatorios e geracao de posts com composicao local e imagem por IA.

O projeto usa arquitetura em camadas e concentra a entrada no Telegram, as regras de negocio em `service/`, a persistencia em `repository/` e o acesso ao PostgreSQL em `database/`.

---

# Funcionalidades

- Cadastro e atualizacao de usuario no primeiro `/start`
- Registro manual de treino em fluxo guiado
- Leitura de imagem de treino via Gemini Vision
- Calculo de pace com entrada validada
- Rankings por quilometragem e por tempo
- Relatorio mensal
- Respostas conversacionais sobre corrida com Gemini
- Geracao de post com layout local
- Geracao adicional de imagem por IA com estilos selecionaveis
- Limite diario e controle simples de taxa para geracao de posts
- Wrapper com reinicio do polling em caso de falha
- Logs estruturados

---

# Arquitetura

```text
Telegram (bot/handlers)
        ↓
Services (service/)
        ↓
Repositories (repository/)
        ↓
PostgreSQL (database/)
```

Separacao principal:

- `bot/`: handlers, estados temporarios, teclados e fluxo de conversa
- `service/`: regras de negocio, orquestracao dos fluxos e integracao com IA
- `repository/`: consultas SQL e persistencia
- `database/`: pool de conexoes
- `image/`: geracao local das imagens de post
- `ia/`: Gemini para chat, analise de treino e geracao de imagem
- `utils/`: logging e utilitarios diversos

---

# Fluxos Principais

## Registro de treino

- O usuario inicia pelo menu ou por comando
- O bot conduz o preenchimento dos dados
- Tambem e possivel enviar uma imagem de treino
- A imagem e analisada pelo `TreinoVisionService`
- Os dados consolidados sao gravados no banco

## Geracao de post

- O usuario escolhe um treino recente
- O bot solicita uma foto
- Sempre e gerada ao menos uma imagem local com `image/post_generator.py`
- Se `GEMINI_ATIVO = True`, o bot pergunta o estilo da imagem IA
- O `PostService` retorna as imagens locais e, quando ativo, tambem a imagem gerada pelo Gemini

Estilos de IA atualmente disponiveis:

- `premium`
- `clean`
- `artistico`
- `cartoon`

---

# Estrutura do Projeto

```text
imwrun/
├── main.py
├── main_test.py
├── wrapper.py
├── README.md
├── requirements.txt
├── assets/
├── bot/
│   ├── handlers/
│   ├── keyboards/
│   ├── state/
│   ├── ui/
│   └── utils/
├── config/
├── database/
├── generated_images/
│   └── teste/
├── ia/
│   ├── gemini.py
│   ├── gemini_image_service.py
│   ├── gemini_prompt.py
│   ├── instrucoes_gemini.txt
│   └── teste_geracao_tipos.py
├── image/
│   ├── layouts/
│   ├── styles/
│   └── utils/
├── repository/
├── service/
├── SQL/
├── temp/
│   └── posts/
└── utils/
    └── logging/
```

Arquivos centrais:

- [main.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos/Projetos%20e%20Dumps/Python/imwrun/main.py): ponto de entrada principal
- [wrapper.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos/Projetos%20e%20Dumps/Python/imwrun/wrapper.py): loop resiliente do bot
- [bot/telegram.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos/Projetos%20e%20Dumps/Python/imwrun/bot/telegram.py): montagem do bot, servicos e handlers
- [service/post_service.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos/Projetos%20e%20Dumps/Python/imwrun/service/post_service.py): orquestracao da geracao de posts
- [ia/gemini_image_service.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos/Projetos%20e%20Dumps/Python/imwrun/ia/gemini_image_service.py): geracao de imagem com Gemini
- [ia/gemini_prompt.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos/Projetos%20e%20Dumps/Python/imwrun/ia/gemini_prompt.py): templates e renderizacao de prompts de imagem

---

# IA no Projeto

## Chat com Gemini

O modulo [ia/gemini.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos/Projetos%20e%20Dumps/Python/imwrun/ia/gemini.py) mantem:

- modelos em fallback para respostas textuais
- historico curto por usuario
- cache simples de respostas
- leitura das instrucoes em `ia/instrucoes_gemini.txt`

## Analise de imagem de treino

O servico [vision_service.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos/Projetos%20e%20Dumps/Python/imwrun/service/vision_service.py) usa Gemini para identificar:

- se a imagem representa um treino
- distancia
- tempo
- pace
- data
- tipo

## Geracao de imagem para post

O servico [gemini_image_service.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos/Projetos%20e%20Dumps/Python/imwrun/ia/gemini_image_service.py) recebe:

- `telegram_id`
- caminho da foto base
- dados do treino
- `prompt_tipo`
- instrucao extra opcional

Os prompts sao centralizados em [gemini_prompt.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos/Projetos%20e%20Dumps/Python/imwrun/ia/gemini_prompt.py) por meio de `PromptTipo` e `render_prompt(...)`.

---

# Banco de Dados

O projeto usa PostgreSQL com pool de conexoes em [database/connection.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos/Projetos%20e%20Dumps/Python/imwrun/database/connection.py).

As credenciais sao carregadas de variaveis de ambiente e o pool e inicializado na montagem do bot.

Arquivos SQL de apoio ficam em `SQL/`.

---

# Instalacao

## 1. Clonar o repositorio

```bash
git clone <repo>
cd imwrun
```

## 2. Criar ambiente virtual

```bash
python -m venv venv
```

Windows:

```powershell
venv\Scripts\activate
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Dependencias principais do projeto:

- `pyTelegramBotAPI`
- `psycopg2-binary`
- `python-dotenv`
- `google-genai`
- `pillow`
- `telegramify-markdown`
- `opencv-python`
- `mediapipe`
- `pandas`
- `openpyxl`

---

# Variaveis de Ambiente

O projeto carrega o `.env` a partir de `c:/Users/x002426/.env` em [config/settings.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos/Projetos%20e%20Dumps/Python/imwrun/config/settings.py).

Variaveis utilizadas:

```env
IMW_HOST=
IMW_PORT=
IMW_DB=
IMW_USER=
IMW_PASS=

BOT_IMWRUNNER=
CHAT_ID=
GROUP_ID=
TELEBOT_TESTE_IA=
GEMINI_TOKEN=

smtp_username_nox=
smtp_password_nox=
smtp_server_nox=
smtp_port_nox=
sender_nox=

smtp_user_prodam=
smtp_password_prodam=
smtp_server_prodam=
smtp_port_prodam=
sender_prodam=

user_gmail=
sender_gmail=
smtp_password_gmail=
smtp_server_gmail=
smtp_port_gmail=
```

---

# Execucao

Execucao principal:

```bash
python main.py
```

Modo alternativo de teste manual:

```bash
python main_test.py
```

O `main.py` usa `BotWrapper`, que reinicia o polling quando ocorre falha no loop principal.

---

# Testes e Scripts de Apoio

No momento o projeto nao possui uma suite automatizada formal com `pytest` ou `unittest`.

Scripts manuais existentes:

- [ia/teste_geracao_tipos.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos%20e%20Dumps/Python/imwrun/ia/teste_geracao_tipos.py): gera imagens para todos os estilos de IA e salva em `generated_images/teste/`
- [ia/teste_de_imagem.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos%20e%20Dumps/Python/imwrun/ia/teste_de_imagem.py): experimento antigo de geracao de imagem
- [ia/teste_de_imagem2.py](/c:/Users/x002426/OneDrive%20-%20rede.sp/Documentos%20e%20Dumps/Python/imwrun/ia/teste_de_imagem2.py): variacao de teste manual de imagem

Exemplo de uso do teste de estilos:

```powershell
./Scripts/python.exe ia/teste_geracao_tipos.py
```

O proprio arquivo aceita configuracao direta no topo, incluindo:

- foto base
- distancia
- tempo
- pace
- instrucao extra

---

# Boas Praticas Aplicadas

- separacao clara entre interface, servicos e persistencia
- pool de conexoes com PostgreSQL
- uso de inteiros para metricas de treino
- logs estruturados
- fallback basico em operacoes de Gemini
- prompts de imagem centralizados por tipo
- fluxo de post com estados temporarios controlados
- geracao em background para nao travar o atendimento do bot

---

# Limitacoes Atuais

- nao ha suite automatizada de testes no repositorio
- `ia/gemini.py` ainda concentra codigo legado e codigo atual no mesmo modulo
- parte dos scripts em `ia/` e experimental
- algumas mensagens e comentarios ainda estao em processo de padronizacao

---

# Melhorias Futuras

- adicionar testes automatizados para prompts, servicos e handlers
- separar melhor o codigo legado de IA
- parametrizar melhor os limites de geracao
- permitir configuracao dinamica dos estilos de post
- expandir os estilos locais de `image/post_generator.py`
- documentar o esquema SQL completo

---

# Licenca

MIT

---

# Autor

Tiago Oliveira Santos
