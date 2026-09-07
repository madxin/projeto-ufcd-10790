from src.dal.players_dal import PlayersDAL


class PlayersBLL:

    @staticmethod
    def get_player_by_discord_id(discord_id):
        return PlayersDAL.get_player_by_discord_id(discord_id)

    @staticmethod
    def remove_player_job(discord_id):
        return PlayersDAL.remove_player_job(discord_id)

    @staticmethod
    def set_player_job(discord_id, job, job_grade):
        return PlayersDAL.set_player_job(
            discord_id,
            job,
            job_grade
        )