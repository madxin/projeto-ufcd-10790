from src.database.server_database import get_server_connection


class PlayersDAL:

    @staticmethod
    def get_player_by_discord_id(discord_id):
        conn = get_server_connection()
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

    @staticmethod
    def remove_player_job(discord_id):
        conn = get_server_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE users
            SET job = 'unemployed',
                job_grade = 0
            WHERE discord_id = %s
        """, (discord_id,))

        conn.commit()

        affected_rows = cursor.rowcount

        cursor.close()
        conn.close()

        return affected_rows > 0