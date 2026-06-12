import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path
from database.database import initialize_database

# Carregar as variáveis do ficheiro .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# Configuração das intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Criar a instância do bot
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# Evento executado quando o bot fica online
@bot.event
async def on_ready():
    print("===================================")
    print("✅ Bot iniciado com sucesso!")
    print(f"🤖 Ligado como: {bot.user}")
    print("===================================")

# Comando de teste
@bot.command()
async def ping(ctx):
    await ctx.send("🏓 Pong!")
# Obter Token
token = os.getenv("TOKEN")
print("TOKEN =", token)

# Inicializar a base de dados
initialize_database()

# Iniciar o bot
bot.run(token)
