import discord
from discord.ext import commands
from src.bll.ticket_settings_bll import TicketSettingsBLL
from datetime import datetime
from src.bll.settings_bll import SettingsBLL
import io

class ConfirmCloseTicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(
        label="✅ Confirmar",
        style=discord.ButtonStyle.green
    )
    async def confirm(
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
                    f"🎫 **Ticket Fechado**\n\n"
                    f"👤 Fechado por: {user.mention}\n"
                    f"📁 Canal: {interaction.channel.name}\n"
                    f"🕒 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
                    file=transcript_file
                )

        await interaction.response.send_message(
            "✅ Ticket fechado.",
            ephemeral=True
        )

        await interaction.channel.delete()

    @discord.ui.button(
        label="❌ Cancelar",
        style=discord.ButtonStyle.grey
    )
    async def cancel(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "❌ Operação cancelada.",
            ephemeral=True
        )

class CloseTicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
    label="🔒 Fechar Ticket",
    style=discord.ButtonStyle.red,
    custom_id="close_ticket"
)
    async def close_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "⚠️ Tem a certeza que pretende fechar este ticket?",
            view=ConfirmCloseTicketView(),
            ephemeral=True
        )


class TicketTypeSelect(discord.ui.Select):

    def __init__(self, guild_id):

        configs = TicketSettingsBLL.get_all_ticket_configs(
            guild_id
        )

        options = []

        for ticket_type, _, _ in configs:

            options.append(
                discord.SelectOption(
                    label=ticket_type.capitalize(),
                    value=ticket_type
                )
            )

        super().__init__(
            placeholder="Escolha o tipo de ticket...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        ticket_type = self.values[0]

        config = TicketSettingsBLL.get_ticket_config(
            interaction.guild.id,
            ticket_type
        )

        if config is None:
            await interaction.response.send_message(
                "❌ Este tipo de ticket não está configurado.",
                ephemeral=True
            )
            return

        category_id, staff_role_id = config

        guild = interaction.guild
        user = interaction.user

        category = guild.get_channel(category_id)
        staff_role = guild.get_role(staff_role_id)

        channel_name = (
            f"{ticket_type}-{user.name}"
            .lower()
            .replace(" ", "-")
        )

        existing_channel = discord.utils.get(
            guild.channels,
            name=channel_name
        )

        if existing_channel:

            await interaction.response.send_message(
                f"❌ Já tens um ticket aberto: {existing_channel.mention}",
                ephemeral=True
            )

            return

        # permissões
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
            f"👋 Olá {user.mention}!\n\n"
            f"Tipo de ticket: **{ticket_type}**\n\n"
            f"Explique o motivo da abertura do ticket.",
            view=CloseTicketView()
        )

        await interaction.response.send_message(
            f"🎫 Escolheste: {ticket_type}",
            ephemeral=True
        )


class TicketTypeView(discord.ui.View):

    def __init__(self, guild_id):

        super().__init__(timeout=180)

        self.add_item(
            TicketTypeSelect(guild_id)
        )        


class TicketPanelView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🎫 Abrir Ticket",
        style=discord.ButtonStyle.green,
        custom_id="open_ticket"
    )
    async def open_ticket(
    self,
    interaction: discord.Interaction,
    button: discord.ui.Button
    ):

        await interaction.response.send_message(
            "Escolha o tipo de ticket:",
            view=TicketTypeView(
                interaction.guild.id
            ),
            ephemeral=True
        )


def setup(bot):

    @bot.command()
    @commands.has_permissions(administrator=True)
    async def ticketpanel(ctx):

        embed = discord.Embed(
            title="🎫 Sistema de Tickets",
            description=(
                "Clique no botão abaixo para abrir um ticket."
            ),
            color=discord.Color.blue()
        )

        await ctx.send(
            embed=embed,
            view=TicketPanelView()
        )