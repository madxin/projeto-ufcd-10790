import discord
from discord.ext import commands


from src.bll.whl_settings_bll import WhlSettingsBLL
import io
from datetime import datetime

from src.bll.settings_bll import SettingsBLL
from src.bll.players_bll import PlayersBLL
from src.bll.whitelist_block_bll import WhitelistBlockBLL

class WhlReviewView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="✅ Aprovar",
        style=discord.ButtonStyle.green
    )
    async def approve(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild
        user = interaction.user

        messages = []

        async for message in interaction.channel.history(
            limit=None,
            oldest_first=True
        ):

            timestamp = message.created_at.strftime(
                "%d/%m/%Y %H:%M:%S"
            )

            content = message.content

            if not content:
                content = "[Mensagem sem texto]"

            messages.append(
                f"[{timestamp}] "
                f"{message.author}: "
                f"{content}"
            )

        transcript_text = "\n".join(messages)

        transcript_file = discord.File(
            io.BytesIO(
                transcript_text.encode("utf-8")
            ),
            filename=f"{interaction.channel.name}.txt"
        )

        logs_channel_id = SettingsBLL.get_logs_channel(
            guild.id
        )

        if logs_channel_id:

            logs_channel = guild.get_channel(
                logs_channel_id
            )

            if logs_channel:

                await logs_channel.send(
                    f"✅ **Candidatura Aprovada**\n\n"
                    f"👤 Aprovada por: {user.mention}\n"
                    f"📁 Canal: {interaction.channel.name}\n"
                    f"🕒 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                    file=transcript_file
                )

        await interaction.response.send_message(
            "✅ Candidatura aprovada.",
            ephemeral=True
        )

        await interaction.channel.delete()

    @discord.ui.button(
        label="❌ Rejeitar",
        style=discord.ButtonStyle.red
    )
    async def reject(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        guild = interaction.guild
        user = interaction.user

        messages = []

        async for message in interaction.channel.history(
            limit=None,
            oldest_first=True
        ):

            timestamp = message.created_at.strftime(
                "%d/%m/%Y %H:%M:%S"
            )

            content = message.content

            if not content:
                content = "[Mensagem sem texto]"

            messages.append(
                f"[{timestamp}] "
                f"{message.author}: "
                f"{content}"
            )

        transcript_text = "\n".join(messages)

        transcript_file = discord.File(
            io.BytesIO(
                transcript_text.encode("utf-8")
            ),
            filename=f"{interaction.channel.name}.txt"
        )

        logs_channel_id = SettingsBLL.get_logs_channel(
            guild.id
        )

        if logs_channel_id:

            logs_channel = guild.get_channel(
                logs_channel_id
            )

            if logs_channel:

                await logs_channel.send(
                    f"❌ **Candidatura Rejeitada**\n\n"
                    f"👤 Rejeitada por: {user.mention}\n"
                    f"📁 Canal: {interaction.channel.name}\n"
                    f"🕒 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                    file=transcript_file
                )

        await interaction.response.send_message(
            "❌ Candidatura rejeitada.",
            ephemeral=True
        )

        await interaction.channel.delete()

class WhlRemoveJobConfirmView(discord.ui.View):

    def __init__(self, whl_type, category_id, staff_role_id, player):
        super().__init__(timeout=60)

        self.whl_type = whl_type
        self.category_id = category_id
        self.staff_role_id = staff_role_id
        self.player = player

    @discord.ui.button(
        label="🗑️ Remover emprego",
        style=discord.ButtonStyle.danger
    )
    async def remove_job(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        job = self.player[4]
        grade = self.player[5]

        embed = discord.Embed(
            title="⚠️ Confirmar remoção",
            description=(
                f"Estás prestes a remover o teu emprego whitelist.\n\n"
                f"**Emprego:** `{job}`\n"
                f"**Grade:** `{grade}`\n\n"
                f"Se confirmares, ficarás como **unemployed** "
                f"e receberás o **Whitelist Block durante 3 dias**.\n\n"
                f"Durante esse período não poderás abrir uma candidatura."
            ),
            color=discord.Color.orange()
        )

        await interaction.response.edit_message(
            embed=embed,
            view=WhlRemoveJobFinalView(
                self.whl_type,
                self.category_id,
                self.staff_role_id,
                self.player
            )
        )

    @discord.ui.button(
        label="❌ Cancelar",
        style=discord.ButtonStyle.secondary
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            content="❌ Operação cancelada.",
            embed=None,
            view=None
        )


class WhlRemoveJobFinalView(discord.ui.View):

    def __init__(self, whl_type, category_id, staff_role_id, player):
        super().__init__(timeout=60)

        self.whl_type = whl_type
        self.category_id = category_id
        self.staff_role_id = staff_role_id
        self.player = player

    @discord.ui.button(
        label="✅ Sim, remover emprego",
        style=discord.ButtonStyle.danger
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        user = interaction.user
        discord_id = str(user.id)

        success = PlayersBLL.remove_player_job(
            discord_id
        )

        if not success:
            await interaction.response.edit_message(
                content="❌ Não foi possível remover o emprego.",
                embed=None,
                view=None
            )
            return

        blocked_until = WhitelistBlockBLL.create_block(
            discord_id
        )

        role_id = WhlSettingsBLL.get_whl_block_role(
            interaction.guild.id
        )

        role = interaction.guild.get_role(role_id)

        if role:
            await user.add_roles(role)

        await interaction.response.edit_message(
            content=(
                "✅ **Emprego removido com sucesso.**\n\n"
                "👤 O teu emprego foi alterado para `unemployed`.\n"
                "🔒 Recebeste o **Whitelist Block durante 3 dias**.\n"
                f"⏰ Bloqueio até: `{blocked_until.strftime('%d/%m/%Y %H:%M')}`\n\n"
                "Depois desse período poderás voltar a candidatar-te."
            ),
            embed=None,
            view=None
        )

    @discord.ui.button(
        label="❌ Não",
        style=discord.ButtonStyle.secondary
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            content="❌ Operação cancelada. O teu emprego não foi alterado.",
            embed=None,
            view=None
        )

class WhlTypeSelect(discord.ui.Select):

    def __init__(self, guild_id):

        configs = WhlSettingsBLL.get_all_whl_configs(
            guild_id
        )

        options = []

        for whl_type, _, _ in configs:

            options.append(
                discord.SelectOption(
                    label=whl_type.capitalize(),
                    value=whl_type
                )
            )

        super().__init__(
            placeholder="Escolha a whitelist...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        whl_type = self.values[0]

        config = WhlSettingsBLL.get_whl_config(
            interaction.guild.id,
            whl_type
        )

        if config is None:

            await interaction.response.send_message(
                "❌ Esta whitelist não está configurada.",
                ephemeral=True
            )

            return

        category_id, staff_role_id = config

        guild = interaction.guild
        user = interaction.user

        player = PlayersBLL.get_player_by_discord_id(
            str(user.id)
        )

        if player is None:
            await interaction.response.send_message(
                "❌ O teu Discord não está associado a nenhum jogador no servidor.",
                ephemeral=True
            )
            return

        job = player[4]
        job_grade = player[5]

        member = interaction.guild.get_member(
            interaction.user.id
        )

        whl_block_role_id = WhlSettingsBLL.get_whl_block_role(
            interaction.guild.id
        )

        has_whl_block = False

        if member and whl_block_role_id:
            has_whl_block = any(
                role.id == whl_block_role_id
                for role in member.roles
            )

        if has_whl_block:
            await interaction.response.send_message(
                "🔒 Estás atualmente em **Whitelist Block** e não podes abrir uma candidatura.",
                ephemeral=True
            )
            return

        if job and job != "unemployed":

            job_label = job

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="⚠️ Emprego encontrado",
                    description=(
                        f"Já tens um emprego whitelist no servidor.\n\n"
                        f"💼 **Emprego:** `{job_label}`\n"
                        f"📊 **Grade:** `{job_grade}`\n\n"
                        "Para iniciares o período de Whitelist Block, "
                        "tens de remover primeiro o teu emprego."
                    ),
                    color=discord.Color.orange()
                ),
                view=WhlRemoveJobConfirmView(
                    whl_type,
                    category_id,
                    staff_role_id,
                    player
                ),
                ephemeral=True
            )

            return

        category = guild.get_channel(
            category_id
        )

        staff_role = guild.get_role(
            staff_role_id
        )

        channel_name = (
            f"wl-{whl_type}-{user.name}"
            .lower()
            .replace(" ", "-")
        )

        existing_channel = discord.utils.get(
            guild.channels,
            name=channel_name
        )

        if existing_channel:

            await interaction.response.send_message(
                f"❌ Já tens uma candidatura aberta: {existing_channel.mention}",
                ephemeral=True
            )

            return
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),

            user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            )
        }

        if staff_role:

            overwrites[staff_role] = (
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    read_message_history=True
                )
            )

            channel = await guild.create_text_channel(
                name=channel_name,
                category=category,
                overwrites=overwrites
            )

            await channel.send(
                f"📋 Bem-vindo {user.mention}\n\n"
                f"**Candidatura: {whl_type.capitalize()}**\n\n"
                f"Por favor responda às seguintes questões:\n\n"
                f"1️⃣ Nome IC\n"
                f"2️⃣ Idade IC\n"
                f"3️⃣ Horas de jogo no servidor\n"
                f"4️⃣ Experiência anterior\n"
                f"5️⃣ Porque deseja integrar esta whitelist?\n\n"
                f"Quando terminar aguarde pela análise da equipa responsável.",
                view=WhlReviewView()
            )

            await interaction.response.send_message(
                f"✅ Candidatura criada: {channel.mention}",
                ephemeral=True
            )


class WhlTypeView(discord.ui.View):

    def __init__(self, guild_id):

        super().__init__(timeout=180)

        self.add_item(
            WhlTypeSelect(guild_id)
        )



class WhlPanelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="📋 Abrir Candidatura",
        style=discord.ButtonStyle.green,
        custom_id="open_whl"
    )
    async def open_whl(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "Escolha a whitelist:",
            view=WhlTypeView(
                interaction.guild.id
            ),
            ephemeral=True
        )


def setup(bot):

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def whlpanel(ctx):

        embed = discord.Embed(
            title="📋 Sistema de Whitelists",
            description=(
                "Clique no botão abaixo para abrir "
                "uma candidatura."
            ),
            color=discord.Color.blue()
        )

        await ctx.send(
            embed=embed,
            view=WhlPanelView()
        )