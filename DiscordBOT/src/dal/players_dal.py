from DiscordBOT.src.database.database import get_connection


class PlayersDAL:

    @staticmethod
    def get_player_by_discord_id(discord_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                identifier,
                discord_id,
                firstname,
                lastname,
                job,
                job_grade,
                `group`
            FROM users
            WHERE discord_id = %s
        """, (discord_id,))

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result