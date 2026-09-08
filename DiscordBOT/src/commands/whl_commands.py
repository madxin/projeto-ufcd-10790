import discord
from discord.ext import commands

from src.bll.whl_settings_bll import WhlSettingsBLL
import io
from datetime import datetime

from src.bll.settings_bll import SettingsBLL
from src.bll.players_bll import PlayersBLL
from src.bll.whitelist_block_bll import WhitelistBlockBLL


class WhlMembersView(discord.ui.View):

    def __init__(self, candidate_id):
        super().__init__(timeout=300)

        self.candidate_id = candidate_id
        self.selected_members = []

        self.member_select = discord.ui.UserSelect(
            placeholder="Seleciona os membros da organização",
            min_values=0,
            max_values=25
        )

        self.member_select.callback = self.select_members
        self.add_item(self.member_select)

    async def select_members(self, interaction: discord.Interaction):

        if interaction.user.id != self.candidate_id:
            await interaction.response.send_message(
                "❌ Apenas o candidato pode indicar os membros da organização.",
                ephemeral=True
            )
            return

        self.selected_members = list(self.member_select.values)

        if not self.selected_members:
            await interaction.response.send_message(
                "✅ Registado: candidatura individual, sem membros.",
                ephemeral=True
            )
            return

        nomes = "\n".join(
            f"• {member.mention}"
            for member in self.selected_members
        )

        await interaction.response.send_message(
            "✅ **Membros da organização registados:**\n\n"
            f"{nomes}",
            ephemeral=True
        )

class WhlApproveModal(discord.ui.Modal):

    def __init__(self, whl_type, members_view):
        super().__init__(
            title="Aprovar Candidatura"
        )

        self.whl_type = whl_type
        self.members_view = members_view

        self.job = discord.ui.TextInput(
            label="Job",
            placeholder="Ex: police",
            required=True,
            max_length=50
        )

        self.grade = discord.ui.TextInput(
            label="Grade",
            placeholder="Ex: 0",
            required=True,
            max_length=10
        )

        self.add_item(self.job)
        self.add_item(self.grade)

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        job = self.job.value.strip()

        try:
            grade = int(
                self.grade.value.strip()
            )

        except ValueError:

            await interaction.response.send_message(
                "❌ A grade tem de ser um número.",
                ephemeral=True
            )

            return

        await interaction.response.defer(
            ephemeral=True
        )

        guild = interaction.guild
        staff_user = interaction.user

        candidate_id = self.members_view.candidate_id
        members = self.members_view.selected_members

        # OBTER CANDIDATO

        candidate = guild.get_member(
            candidate_id
        )

        if candidate is None:

            await interaction.followup.send(
                "❌ Não foi possível encontrar o candidato no Discord.",
                ephemeral=True
            )

            return

        # OBTER CONFIGURAÇÃO

        config = WhlSettingsBLL.get_whl_config(
            guild.id,
            self.whl_type
        )

        if config is None:

            await interaction.followup.send(
                "❌ A configuração desta whitelist não foi encontrada.",
                ephemeral=True
            )

            return

        category_id, staff_role_id, organization_role_id = config

        # CARGO DA ORGANIZAÇÃO

        organization_role = guild.get_role(
            organization_role_id
        )

        if organization_role is None:

            await interaction.followup.send(
                "❌ O cargo da organização configurado para esta whitelist não existe.",
                ephemeral=True
            )

            return

        # ATUALIZAR CANDIDATO

        candidate_updated = PlayersBLL.set_player_job(
            str(candidate.id),
            job,
            grade
        )

        if not candidate_updated:

            await interaction.followup.send(
                "❌ Não foi possível atualizar o emprego do candidato.",
                ephemeral=True
            )

            return

        try:

            await candidate.add_roles(
                organization_role,
                reason=f"Whitelist {self.whl_type} aprovada"
            )

        except discord.Forbidden:

            await interaction.followup.send(
                "❌ Não tenho permissões para atribuir o cargo da organização ao candidato.",
                ephemeral=True
            )

            return

        # PROCESSAR MEMBROS

        approved_members = []
        ignored_members = []

        whl_block_role_id = SettingsBLL.get_whl_block_role(
            guild.id
        )

        for member in members:

            if member.id == candidate.id:
                continue

            player = PlayersBLL.get_player_by_discord_id(
                str(member.id)
            )

            if player is None:

                ignored_members.append(
                    f"{member.mention} — jogador não encontrado"
                )

                continue

            current_job = player[4]

            has_whl_block = False

            if whl_block_role_id:

                has_whl_block = any(
                    role.id == whl_block_role_id
                    for role in member.roles
                )

            if has_whl_block:

                ignored_members.append(
                    f"{member.mention} — Whitelist Block"
                )

                continue

            if current_job and current_job != "unemployed":

                ignored_members.append(
                    f"{member.mention} — já possui o job `{current_job}`"
                )

                continue

            member_updated = PlayersBLL.set_player_job(
                str(member.id),
                job,
                0
            )

            if not member_updated:

                ignored_members.append(
                    f"{member.mention} — não foi possível atualizar o job"
                )

                continue

            try:

                await member.add_roles(
                    organization_role,
                    reason=f"Membro da organização {self.whl_type}"
                )

                approved_members.append(
                    member.mention
                )

            except discord.Forbidden:

                ignored_members.append(
                    f"{member.mention} — sem permissões para atribuir cargo"
                )

        # TRANSCRIPT

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

        transcript_text = "\n".join(
            messages
        )

        transcript_file = discord.File(
            io.BytesIO(
                transcript_text.encode("utf-8")
            ),
            filename=f"{interaction.channel.name}.txt"
        )

        # LOGS


        logs_channel_id = SettingsBLL.get_logs_channel(
            guild.id
        )

        if logs_channel_id:

            logs_channel = guild.get_channel(
                logs_channel_id
            )

            if logs_channel:

                approved_text = (
                    "\n".join(
                        f"• {member}"
                        for member in approved_members
                    )
                    if approved_members
                    else "Nenhum membro adicional."
                )

                ignored_text = (
                    "\n".join(
                        f"• {member}"
                        for member in ignored_members
                    )
                    if ignored_members
                    else "Nenhum membro ignorado."
                )

                await logs_channel.send(
                    f"✅ **Candidatura Aprovada**\n\n"
                    f"👤 **Candidato:** {candidate.mention}\n"
                    f"👨‍💼 **Aprovada por:** {staff_user.mention}\n"
                    f"📁 **Whitelist:** `{self.whl_type}`\n"
                    f"💼 **Job:** `{job}`\n"
                    f"📊 **Grade:** `{grade}`\n\n"
                    f"👥 **Membros aprovados:**\n"
                    f"{approved_text}\n\n"
                    f"⚠️ **Membros ignorados:**\n"
                    f"{ignored_text}\n\n"
                    f"🕒 **Data:** "
                    f"{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                    file=transcript_file
                )

        # RESPOSTA FINAL

        approved_count = len(
            approved_members
        )

        ignored_count = len(
            ignored_members
        )

        await interaction.followup.send(
            f"✅ **Candidatura aprovada com sucesso!**\n\n"
            f"👤 **Candidato:** {candidate.mention}\n"
            f"💼 **Job:** `{job}`\n"
            f"📊 **Grade:** `{grade}`\n"
            f"🎭 **Cargo:** {organization_role.mention}\n\n"
            f"👥 **Membros aprovados:** `{approved_count}`\n"
            f"⚠️ **Membros ignorados:** `{ignored_count}`",
            ephemeral=True
        )

        await interaction.channel.delete()

class WhlReviewView(discord.ui.View):

    def __init__(self, whl_type, members_view):
        super().__init__(timeout=None)

        self.whl_type = whl_type
        self.members_view = members_view

    def has_staff_permission(self, interaction):

        config = WhlSettingsBLL.get_whl_config(
            interaction.guild.id,
            self.whl_type
        )

        if config is None:
            return False

        _, staff_role_id, _ = config

        staff_role = interaction.guild.get_role(
            staff_role_id
        )

        if staff_role is None:
            return False

        return staff_role in interaction.user.roles

    @discord.ui.button(
        label="✅ Aprovar",
        style=discord.ButtonStyle.green
    )
    async def approve(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not self.has_staff_permission(interaction):

            await interaction.response.send_message(
                "❌ Não tens permissões para analisar esta candidatura.",
                ephemeral=True
            )

            return

        await interaction.response.send_modal(
            WhlApproveModal(
                self.whl_type,
                self.members_view
            )
        )

    @discord.ui.button(
        label="❌ Rejeitar",
        style=discord.ButtonStyle.red
    )
    async def reject(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if not self.has_staff_permission(interaction):

            await interaction.response.send_message(
                "❌ Não tens permissões para analisar esta candidatura.",
                ephemeral=True
            )

            return

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

    def __init__(
        self,
        whl_type,
        category_id,
        staff_role_id,
        player
    ):
        super().__init__(timeout=180)

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

    def __init__(
        self,
        whl_type,
        category_id,
        staff_role_id,
        player
    ):
        super().__init__(timeout=180)

        self.whl_type = whl_type
        self.category_id = category_id
        self.staff_role_id = staff_role_id
        self.player = player

        self.selected_role = None

        self.role_select = discord.ui.RoleSelect(
            placeholder="Seleciona o cargo da organização",
            min_values=1,
            max_values=1
        )

        self.role_select.callback = self.select_role

        self.add_item(self.role_select)

    async def select_role(
        self,
        interaction: discord.Interaction
    ):

        self.selected_role = self.role_select.values[0]

        await interaction.response.send_message(
            f"🎭 Cargo selecionado: {self.selected_role.mention}\n\n"
            "Agora podes confirmar a remoção do emprego.",
            ephemeral=True
        )

    @discord.ui.button(
        label="✅ Sim, remover emprego",
        style=discord.ButtonStyle.danger,
        row=1
    )
    async def confirm(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        if self.selected_role is None:

            await interaction.response.send_message(
                "❌ Primeiro tens de selecionar o cargo da organização que queres remover.",
                ephemeral=True
            )

            return

        user = interaction.user
        discord_id = str(user.id)

        # Remover o emprego da BD
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

        # Remover o cargo da organização
        try:

            await user.remove_roles(
                self.selected_role,
                reason="Entrada em Whitelist Block"
            )

        except discord.Forbidden:

            await interaction.response.edit_message(
                content=(
                    "❌ O emprego foi removido, mas não tenho "
                    "permissões para remover o cargo Discord selecionado."
                ),
                embed=None,
                view=None
            )

            return

        # Criar Whitelist Block
        blocked_until = WhitelistBlockBLL.create_block(
            discord_id
        )

        # Obter cargo Whitelist Block
        role_id = SettingsBLL.get_whl_block_role(
            interaction.guild.id
        )

        role = interaction.guild.get_role(
            role_id
        )

        if role:

            try:

                await user.add_roles(
                    role,
                    reason="Entrada em Whitelist Block"
                )

            except discord.Forbidden:

                await interaction.response.edit_message(
                    content=(
                        "⚠️ O emprego e o cargo da organização foram removidos, "
                        "mas não tenho permissões para atribuir o Whitelist Block."
                    ),
                    embed=None,
                    view=None
                )

                return

        await interaction.response.edit_message(
            content=(
                "✅ **Emprego removido com sucesso.**\n\n"
                "👤 O teu emprego foi alterado para `unemployed`.\n"
                f"🎭 Cargo removido: {self.selected_role.mention}\n"
                "🔒 Recebeste o **Whitelist Block durante 3 dias**.\n"
                f"⏰ Bloqueio até: "
                f"`{blocked_until.strftime('%d/%m/%Y %H:%M')}`\n\n"
                "Depois desse período poderás voltar a candidatar-te."
            ),
            embed=None,
            view=None
        )

    @discord.ui.button(
        label="❌ Não",
        style=discord.ButtonStyle.secondary,
        row=1
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.edit_message(
            content=(
                "❌ Operação cancelada. "
                "O teu emprego não foi alterado."
            ),
            embed=None,
            view=None
        )


class WhlTypeSelect(discord.ui.Select):

    def __init__(self, guild):

        configs = WhlSettingsBLL.get_all_whl_configs(
            guild.id
        )

        options = []

        for whl_type, _, _, organization_role_id in configs:

            organization_role = guild.get_role(
                organization_role_id
            )

            if organization_role:

                label = organization_role.name

            else:

                label = whl_type.capitalize()

            options.append(
                discord.SelectOption(
                    label=label,
                    value=whl_type
                )
            )

        super().__init__(
            placeholder="Escolha uma organização...",
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

        category_id, staff_role_id, organization_role_id = config

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

        whl_block_role_id = SettingsBLL.get_whl_block_role(
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

        members_view = WhlMembersView(user.id)

        await channel.send(
            f"📋 Bem-vindo {user.mention}\n\n"
            f"**Candidatura: {whl_type.capitalize()}**\n\n"
            f"Por favor responda às seguintes questões:\n\n"
            f"1️⃣ Nome IC\n"
            f"2️⃣ Idade IC\n"
            f"3️⃣ Horas de jogo no servidor\n"
            f"4️⃣ Experiência anterior\n"
            f"5️⃣ Porque deseja integrar esta whitelist?\n\n"
            f"Quando terminar, indique os membros da organização.",
            view=members_view
        )

        await channel.send(
            "👨‍💼 **Análise da candidatura**\n\n"
            "A equipa responsável irá analisar esta candidatura.",
            view=WhlReviewView(
                whl_type,
                members_view
            )
        )

        await interaction.response.send_message(
            f"✅ Candidatura criada: {channel.mention}",
            ephemeral=True
        )


class WhlTypeView(discord.ui.View):

    def __init__(self, guild):

        super().__init__(timeout=180)

        self.add_item(
            WhlTypeSelect(guild)
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
            "Escolha a organização:",
            view=WhlTypeView(
                interaction.guild
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
        