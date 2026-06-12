from database.database import get_connection

class SettingsDAL:

    @staticmethod
    def set_autorole(guild_id: int, role_id: int):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO settings (guild_id, autorole_id)
            VALUES (?, ?)
        """, (guild_id, role_id))

        conn.commit()
        conn.close()

    @staticmethod
    def get_autorole(guild_id: int):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT autorole_id
            FROM settings
            WHERE guild_id = ?
        """, (guild_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]

        return None