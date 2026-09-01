import discord
from discord.ext import commands

from config import TOKEN
from src.database.database import initialize_database

from src.commands.admin_commands import setup as setup_admin_commands
from src.commands.ticket_commands import setup as setup_ticket_commands
from src.commands.whl_commands import setup as setup_whl_commands
from src.events.member_events import setup as setup_member_events


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
    print(f"🌍 Servidores: {len(bot.guilds)}")
    print("===================================")


# Comando de teste

@bot.command()
async def ping(ctx):

    await ctx.send("🏓 Pong!")


# Carregar comandos e eventos

setup_admin_commands(bot)
setup_member_events(bot)
setup_ticket_commands(bot)
setup_whl_commands(bot)


# Inicializar a base de dados

initialize_database()


# Iniciar o bot

bot.run(TOKEN)