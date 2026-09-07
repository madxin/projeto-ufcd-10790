from datetime import datetime
from discord.errors import Forbidden

from src.bll.settings_bll import SettingsBLL
from src.bll.whitelist_block_bll import WhitelistBlockBLL


class MemberBLL:

    @staticmethod
    async def on_member_join(member):

        discord_id = str(member.id)

        block = WhitelistBlockBLL.get_block(discord_id)

        if block is not None:

            blocked_until = block[1]

            if datetime.now() < blocked_until:

                role_id = SettingsBLL.get_whl_block_role(
                    member.guild.id
                )

                if role_id:

                    role = member.guild.get_role(role_id)

                    if role:

                        try:

                            await member.add_roles(role)

                            print(
                                f"🔒 {member.name} voltou ao servidor "
                                f"e recebeu novamente o WhitelistBlock."
                            )

                        except Forbidden:

                            print(
                                "❌ O bot não tem permissões para "
                                "atribuir o WhitelistBlock."
                            )

                        except Exception as e:

                            print(
                                f"❌ Erro ao atribuir WhitelistBlock: {e}"
                            )

            else:

                WhitelistBlockBLL.remove_block(discord_id)

        # Autorole
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