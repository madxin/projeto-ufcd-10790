import discord
from discord.ext import commands

from src.bll.whl_settings_bll import WhlSettingsBLL


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
                f"Quando terminar aguarde pela análise da equipa responsável."
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