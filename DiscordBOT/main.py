import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from pathlib import Path
from database.database import initialize_database
from src.dal.settings_dal import SettingsDAL

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

###AUTOROLE###

# Autorole
@bot.command()
@commands.has_permissions(administrator=True)
async def setautorole(ctx, role: discord.Role):

    SettingsDAL.set_autorole(
        guild_id=ctx.guild.id,
        role_id=role.id
    )

    await ctx.send(
        f"✅ O cargo automático foi configurado para {role.mention}."
    )

# Entrada de Novos Membros
@bot.event
async def on_member_join(member):

    role_id = SettingsDAL.get_autorole(member.guild.id)

    if role_id is None:
        return

    role = member.guild.get_role(role_id)

    if role:
        await member.add_roles(role)
        print(f"{member.name} recebeu o cargo {role.name}.")

# Comando para ver o set de Autorole
@bot.command()
async def autorole(ctx):

    role_id = SettingsDAL.get_autorole(ctx.guild.id)

    if role_id is None:
        await ctx.send("❌ Não existe nenhum cargo automático configurado.")
        return

    role = ctx.guild.get_role(role_id)

    if role:
        await ctx.send(
            f"📋 O cargo automático atual é: {role.mention}"
        )
    else:
        await ctx.send(
            "⚠️ O cargo configurado já não existe no servidor."
        )

# Comando para resetar o Autorole
@bot.command()
@commands.has_permissions(administrator=True)
async def clearautorole(ctx):

    SettingsDAL.clear_autorole(ctx.guild.id)

    await ctx.send(
        "🗑️ O cargo automático foi removido com sucesso."
    )

###LOGS###

# Escolher o canal das logs
@bot.command()
@commands.has_permissions(administrator=True)
async def setlogschannel(ctx, channel: discord.TextChannel):

    SettingsDAL.set_logs_channel(
        guild_id=ctx.guild.id,
        channel_id=channel.id
    )

    await ctx.send(
        f"✅ O canal de logs foi configurado para {channel.mention}."
    )

# Comando para testar o canal das logs
@bot.command()
async def logschannel(ctx):

    channel_id = SettingsDAL.get_logs_channel(ctx.guild.id)

    if channel_id is None:
        await ctx.send("❌ Nenhum canal de logs está configurado.")
        return

    channel = ctx.guild.get_channel(channel_id)

    if channel:
        await ctx.send(
            f"📋 O canal de logs atual é: {channel.mention}"
        )
    else:
        await ctx.send(
            "⚠️ O canal configurado já não existe."
        )

# Obter Token
token = os.getenv("TOKEN")
print("TOKEN =", token)

# Inicializar a base de dados
initialize_database()


# Iniciar o bot
bot.run(token)
