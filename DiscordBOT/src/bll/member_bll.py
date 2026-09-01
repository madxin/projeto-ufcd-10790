from discord.errors import Forbidden

from src.bll.settings_bll import SettingsBLL


class MemberBLL:

    @staticmethod
    async def on_member_join(member):

        role_id = SettingsBLL.get_autorole(
            member.guild.id
        )

        if role_id is None:
            return

        role = member.guild.get_role(role_id)

        if role is None:

            print(
                f"⚠️ O cargo com ID {role_id} já não existe."
            )

            return

        try:

            await member.add_roles(role)

            print(
                f"✅ {member.name} recebeu o cargo {role.name}."
            )

        except Forbidden:

            print(
                "❌ O bot não tem permissões para atribuir este cargo."
            )

        except Exception as e:

            print(
                f"❌ Erro ao atribuir cargo: {e}"
            )