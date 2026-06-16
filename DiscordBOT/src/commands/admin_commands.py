import discord
from discord.ext import commands

from src.bll.settings_bll import SettingsBLL
from src.bll.ticket_settings_bll import TicketSettingsBLL


def setup(bot):
    ### CARGOS
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

    ### LOGS
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
   
    ### TICKETS
    @bot.command()
    @commands.has_permissions(administrator=True)
    async def setticketcategory(
        ctx,
        ticket_type: str,
        *,
        category_name: str
    ):

        category = discord.utils.get(
            ctx.guild.categories,
            name=category_name
        )

        if category is None:
            await ctx.send(
                f"❌ A categoria '{category_name}' não foi encontrada."
            )
            return

        TicketSettingsBLL.set_ticket_category(
            ctx.guild.id,
            ticket_type,
            category.id
        )

        await ctx.send(
            f"✅ Categoria do ticket **{ticket_type}** configurada para **{category.name}**."
        )

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def setticketrole(
        ctx,
        ticket_type: str,
        role: discord.Role
    ):

        TicketSettingsBLL.set_ticket_role(
            ctx.guild.id,
            ticket_type,
            role.id
        )

        await ctx.send(
            f"✅ Cargo do ticket **{ticket_type}** configurado para {role.mention}."
        )

    @bot.command()
    async def ticketconfig(ctx):

        configs = TicketSettingsBLL.get_all_ticket_configs(
            ctx.guild.id
        )

        if not configs:
            await ctx.send(
                "❌ Não existem configurações de tickets."
            )
            return

        mensagem = "## 🎫 Configuração dos Tickets\n\n"

        for ticket_type, category_id, role_id in configs:

            category = ctx.guild.get_channel(category_id) if category_id else None
            role = ctx.guild.get_role(role_id) if role_id else None

            mensagem += (
                f"**{ticket_type.capitalize()}**\n"
                f"📂 Categoria: "
                f"{category.name if category else 'Não configurada'}\n"
                f"👮 Cargo: "
                f"{role.mention if role else 'Não configurado'}\n\n"
            )

        await ctx.send(mensagem)        