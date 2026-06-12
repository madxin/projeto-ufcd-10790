from src.bll.settings_bll import SettingsBLL


def setup(bot):

    @bot.event
    async def on_member_join(member):

        role_id = SettingsBLL.get_autorole(
            member.guild.id
        )

        if role_id is None:
            return

        role = member.guild.get_role(role_id)

        if role:
            await member.add_roles(role)
            print(
                f"{member.name} recebeu o cargo {role.name}."
            )