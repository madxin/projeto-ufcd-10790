import discord
from discord.ext import commands

from src.bll.settings_bll import SettingsBLL
from src.bll.ticket_settings_bll import TicketSettingsBLL
from src.bll.whl_settings_bll import WhlSettingsBLL
from src.bll.players_bll import PlayersBLL
from src.bll.whitelist_block_bll import WhitelistBlockBLL


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
                f"👨‍💼 Cargo: "
                f"{role.mention if role else 'Não configurado'}\n\n"
            )

        await ctx.send(mensagem)

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def setwhlcategory(
        ctx,
        whl_type: str,
        *args
    ):

        if len(args) < 2:
            await ctx.send(
                "❌ Utilização correta:\n"
                "`!setwhlcategory <tipo> <categoria> <cargo>`"
            )
            return

        organization_role = None

        # O último argumento tem de ser um cargo
        role_text = args[-1]

        if ctx.message.role_mentions:
            for role in ctx.message.role_mentions:
                if role.mention == role_text:
                    organization_role = role
                    break

        if organization_role is None:
            await ctx.send(
                "❌ Tens de mencionar um cargo da organização no final do comando."
            )
            return

        category_name = " ".join(args[:-1]).strip()

        category = discord.utils.get(
            ctx.guild.categories,
            name=category_name
        )

        if category is None:
            await ctx.send(
                f"❌ A categoria '{category_name}' não foi encontrada."
            )
            return

        WhlSettingsBLL.set_whl_category(
            ctx.guild.id,
            whl_type,
            category.id,
            organization_role.id
        )

        await ctx.send(
            f"✅ Whitelist **{whl_type}** configurada.\n\n"
            f"📂 Categoria: {category.name}\n"
            f"🏢 Cargo da organização: {organization_role.mention}"
        )

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def setwhlrole(
        ctx,
        whl_type: str,
        role: discord.Role
    ):

        WhlSettingsBLL.set_whl_role(
            ctx.guild.id,
            whl_type,
            role.id
        )

        await ctx.send(
            f"✅ Cargo da whitelist **{whl_type}** configurado para {role.mention}."
        )

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def whlconfig(ctx):

        configs = WhlSettingsBLL.get_all_whl_configs(
            ctx.guild.id
        )

        if not configs:

            await ctx.send(
                "❌ Não existem configurações de whitelist."
            )

            return

        mensagens = []
        mensagem_atual = "⚙️ **Configuração das Whitelists**\n\n"

        for (
            whl_type,
            category_id,
            staff_role_id,
            organization_role_id
        ) in configs:

            category = ctx.guild.get_channel(
                category_id
            )

            staff_role = ctx.guild.get_role(
                staff_role_id
            )

            organization_role = ctx.guild.get_role(
                organization_role_id
            )

            category_text = (
                category.mention
                if category
                else f"`{category_id}`"
            )

            staff_text = (
                staff_role.mention
                if staff_role
                else f"`{staff_role_id}`"
            )

            organization_text = (
                organization_role.mention
                if organization_role
                else f"`{organization_role_id}`"
            )

            bloco = (
                f"📋 **{whl_type.capitalize()}**\n"
                f"└ 📁 Categoria: {category_text}\n"
                f"└ 👨‍💼 Staff: {staff_text}\n"
                f"└ 🏢 Organização: {organization_text}\n\n"
            )

            if len(mensagem_atual) + len(bloco) > 1900:

                mensagens.append(
                    mensagem_atual
                )

                mensagem_atual = bloco

            else:

                mensagem_atual += bloco

        if mensagem_atual:

            mensagens.append(
                mensagem_atual
            )

        for mensagem in mensagens:

            await ctx.send(
                mensagem
            )

        ### PLAYERS

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def player(ctx, member: discord.Member = None):

        if member is None:
            member = ctx.author

        discord_id = str(member.id)

        player = PlayersBLL.get_player_by_discord_id(
            discord_id
        )

        if player is None:
            await ctx.send(
                f"❌ O Discord de {member.mention} não está associado a nenhum jogador."
            )
            return

        (
            identifier,
            discord_id,
            firstname,
            lastname,
            job,
            job_grade,
            group
        ) = player

        await ctx.send(
            f"## 👤 Informação do Jogador\n\n"
            f"**Discord:** {member.mention}\n"
            f"**Nome:** {firstname} {lastname}\n"
            f"**Discord ID:** {discord_id}\n"
            f"**Identifier:** `{identifier}`\n"
            f"**Job:** {job}\n"
            f"**Job Grade:** {job_grade}\n"
            f"**Grupo:** {group}"
        )

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def clearwhlblock(ctx, member: discord.Member):

        discord_id = str(member.id)

        WhitelistBlockBLL.remove_block(
            discord_id
        )

        role_id = SettingsBLL.get_whl_block_role(
            ctx.guild.id
        )

        role = ctx.guild.get_role(role_id) if role_id else None

        if role and role in member.roles:
            await member.remove_roles(role)

        await ctx.send(
            f"✅ O Whitelist Block de {member.mention} foi removido."
        )

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def setwhlblock(ctx, role: discord.Role):

        SettingsBLL.set_whl_block_role(
            ctx.guild.id,
            role.id
        )

        await ctx.send(
            f"✅ O cargo de Whitelist Block foi configurado para {role.mention}."
        )

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def whlblockconfig(ctx):

        role_id = SettingsBLL.get_whl_block_role(
            ctx.guild.id
        )

        if role_id is None:
            await ctx.send(
                "❌ Nenhum cargo de Whitelist Block está configurado."
            )
            return

        role = ctx.guild.get_role(role_id)

        if role is None:
            await ctx.send(
                "⚠️ O cargo configurado já não existe neste servidor."
            )
            return

        await ctx.send(
            f"🔒 **Whitelist Block**\n\n"
            f"Cargo configurado: {role.mention}"
        )        