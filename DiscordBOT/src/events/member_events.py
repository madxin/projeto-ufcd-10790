from src.bll.member_bll import MemberBLL


def setup(bot):

    @bot.event
    async def on_member_join(member):

        await MemberBLL.on_member_join(member)