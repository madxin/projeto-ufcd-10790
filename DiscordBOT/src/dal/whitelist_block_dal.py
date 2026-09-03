from src.database.database import get_connection


class WhitelistBlockDAL:

    @staticmethod
    def get_block(discord_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT discord_id, blocked_until
            FROM whitelist_blocks
            WHERE discord_id = %s
        """, (discord_id,))

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result

    @staticmethod
    def set_block(discord_id, blocked_until):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO whitelist_blocks
                (discord_id, blocked_until)
            VALUES
                (%s, %s)
            ON DUPLICATE KEY UPDATE
                blocked_until = VALUES(blocked_until)
        """, (discord_id, blocked_until))

        conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def remove_block(discord_id):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM whitelist_blocks
            WHERE discord_id = %s
        """, (discord_id,))

        conn.commit()

        cursor.close()
        conn.close()