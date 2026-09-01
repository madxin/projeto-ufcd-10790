from src.database.database import get_connection


class SettingsDAL:

    @staticmethod
    def set_autorole(
        guild_id: int,
        role_id: int
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO settings (
                guild_id,
                autorole_id
            )
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                autorole_id = VALUES(autorole_id)
        """, (
            guild_id,
            role_id
        ))

        conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def get_autorole(
        guild_id: int
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                autorole_id
            FROM settings
            WHERE guild_id = %s
        """, (
            guild_id,
        ))

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0]

        return None

    @staticmethod
    def clear_autorole(
        guild_id: int
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE settings
            SET autorole_id = NULL
            WHERE guild_id = %s
        """, (
            guild_id,
        ))

        conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def set_logs_channel(
        guild_id: int,
        channel_id: int
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO settings (
                guild_id,
                logs_channel_id
            )
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE
                logs_channel_id = VALUES(logs_channel_id)
        """, (
            guild_id,
            channel_id
        ))

        conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def get_logs_channel(
        guild_id: int
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                logs_channel_id
            FROM settings
            WHERE guild_id = %s
        """, (
            guild_id,
        ))

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0]

        return None