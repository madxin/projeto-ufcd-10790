import discord
from discord.ext import commands

from src.bll.settings_bll import SettingsBLL


def setup(bot):

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def setautorole(ctx, role: discord.Role):
        SettingsBLL.set_autorole(ctx.guild.id, role.id)
        await ctx.send(
            f"✅ O cargo automático foi configurado para {role.mention}."
        )

    @bot.command()
    async def autorole(ctx):
        role_id = SettingsBLL.get_autorole(ctx.guild.id)

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
                "⚠️ O cargo configurado já não existe."
            )

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def clearautorole(ctx):
        SettingsBLL.clear_autorole(ctx.guild.id)
        await ctx.send(
            "🗑️ O cargo automático foi removido."
        )

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def setlogschannel(ctx, channel: discord.TextChannel):
        SettingsBLL.set_logs_channel(
            ctx.guild.id,
            channel.id
        )

        await ctx.send(
            f"✅ Canal de logs configurado para {channel.mention}."
        )

    @bot.command()
    async def logschannel(ctx):
        channel_id = SettingsBLL.get_logs_channel(ctx.guild.id)

        if channel_id is None:
            await ctx.send(
                "❌ Nenhum canal de logs está configurado."
            )
            return

        channel = ctx.guild.get_channel(channel_id)

        if channel:
            await ctx.send(
                f"📋 O canal de logs atual é: {channel.mention}"
            )