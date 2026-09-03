from src.dal.players_dal import PlayersDAL


class PlayersBLL:

    @staticmethod
    def get_player_by_discord_id(discord_id):
        return PlayersDAL.get_player_by_discord_id(discord_id)