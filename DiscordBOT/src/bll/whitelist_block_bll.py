from datetime import datetime, timedelta

from src.dal.whitelist_block_dal import WhitelistBlockDAL


class WhitelistBlockBLL:

    @staticmethod
    def get_block(discord_id):
        return WhitelistBlockDAL.get_block(discord_id)

    @staticmethod
    def create_block(discord_id):
        blocked_until = datetime.now() + timedelta(days=3)

        WhitelistBlockDAL.set_block(
            discord_id,
            blocked_until
        )

        return blocked_until

    @staticmethod
    def remove_block(discord_id):
        WhitelistBlockDAL.remove_block(discord_id)

    @staticmethod
    def is_blocked(discord_id):
        block = WhitelistBlockDAL.get_block(discord_id)

        if block is None:
            return False

        blocked_until = block[1]

        if datetime.now() >= blocked_until:
            WhitelistBlockDAL.remove_block(discord_id)
            return False

        return True