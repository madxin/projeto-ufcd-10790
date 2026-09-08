# MWRP-BOT – Sistema de Gestão para Servidor Discord

Bot de Discord desenvolvido em Python para gestão e automatização de processos administrativos num servidor de Roleplay.

## Funcionalidades

- Sistema de Tickets
- Sistema de Whitelist
- Gestão de organizações
- Gestão de membros
- Atribuição automática de cargos Discord
- Gestão de `job` e `job_grade`
- Integração com a base de dados MySQL `s1_data`
- Sistema de Whitelist Block
- Logs administrativos
- Transcrições de tickets
- Autorole
- Configuração das funcionalidades através do Discord

## Tecnologias

- Python
- discord.py
- MySQL
- SQLite
- python-dotenv

## Estrutura do Projeto

DiscordBOT/
├── src/
│   ├── bll/
│   │   ├── member_bll.py
│   │   ├── players_bll.py
│   │   ├── settings_bll.py
│   │   ├── ticket_settings_bll.py
│   │   ├── whitelist_block_bll.py
│   │   └── whl_settings_bll.py
│   │
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── admin_commands.py
│   │   ├── ticket_commands.py
│   │   └── whl_commands.py
│   │
│   ├── dal/
│   │   ├── players_dal.py
│   │   ├── settings_dal.py
│   │   ├── ticket_settings_dal.py
│   │   ├── whitelist_block_dal.py
│   │   └── whl_settings_dal.py
│   │
│   ├── database/
│   │   ├── database.py
│   │   └── server_database.py
│   │
│   └── events/
│       ├── __init__.py
│       └── member_events.py
│
├── .env
├── config.py
├── LEIA-ME.md
├── main.py
└── requirements.txt

## Arquitetura

O projeto utiliza uma arquitetura em camadas:

Commands / Events
        ↓
       BLL
        ↓
       DAL
        ↓
    Database

- Commands – comandos e interações do Discord.
- Events – eventos automáticos do Discord.
- BLL – lógica de negócio do sistema.
- DAL – acesso às bases de dados.
- Database – gestão das ligações às bases de dados.

## Base de Dados

O sistema utiliza bases de dados para armazenar as configurações e informações necessárias ao funcionamento do bot.

Existe também uma ligação à base de dados MySQL `s1_data` do servidor RP, utilizada para consultar e atualizar os dados dos jogadores, incluindo:

- `discord_id`
- `job`
- `job_grade`

## Segurança

- As credenciais e o token do Discord são armazenados no ficheiro `.env`.
- O ficheiro `.env` está protegido pelo `.gitignore` e não é incluído no repositório.
- As queries SQL utilizam parâmetros para reduzir o risco de SQL Injection.
- As funcionalidades administrativas possuem controlo de permissões.
- As operações de Whitelist verificam o estado do jogador antes de realizar alterações.

## Instalação

Criar um ambiente virtual:

python -m venv .venv

Ativar o ambiente virtual no Windows:

.venv\Scripts\Activate.ps1

Instalar as dependências:

pip install -r requirements.txt

## Configuração

Antes de executar o bot, é necessário configurar o ficheiro `.env` com o token do Discord e os dados de acesso às bases de dados.

O ficheiro `.env` não deve ser partilhado nem enviado para o repositório.

## Execução

Depois de instalar as dependências e configurar o `.env`, executar:

python main.py

## Autor

**Carlos Madaleno**

Projeto desenvolvido no âmbito da **UFCD 5425**.