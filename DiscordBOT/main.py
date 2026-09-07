import discord
from discord.ext import commands, tasks

from config import TOKEN
from src.database.database import initialize_database


from src.commands.admin_commands import setup as setup_admin_commands
from src.commands.ticket_commands import setup as setup_ticket_commands
from src.commands.whl_commands import setup as setup_whl_commands
from src.events.member_events import setup as setup_member_events
from src.bll.whitelist_block_bll import WhitelistBlockBLL
from src.bll.settings_bll import SettingsBLL


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

@tasks.loop(minutes=1)
async def check_expired_whitelist_blocks():

    expired_blocks = WhitelistBlockBLL.get_expired_blocks()

    for discord_id, blocked_until in expired_blocks:

        for guild in bot.guilds:

            member = guild.get_member(int(discord_id))

            if member is None:
                continue

            role_id = SettingsBLL.get_whl_block_role(guild.id)

            if role_id is None:
                continue

            role = guild.get_role(role_id)

            if role and role in member.roles:
                await member.remove_roles(role)

        WhitelistBlockBLL.remove_block(discord_id)

@bot.event
async def on_ready():

    print("===================================")
    print("✅ Bot iniciado com sucesso!")
    print(f"🤖 Ligado como: {bot.user}")
    print(f"🌍 Servidores: {len(bot.guilds)}")
    print("===================================")

    if not check_expired_whitelist_blocks.is_running():
        check_expired_whitelist_blocks.start()


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