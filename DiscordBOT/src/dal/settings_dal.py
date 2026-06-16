from database.database import get_connection

class SettingsDAL:

    @staticmethod
    def set_autorole(guild_id: int, role_id: int): #Funçao Autorole
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO settings (guild_id, autorole_id)
            VALUES (?, ?)
        """, (guild_id, role_id))

        conn.commit()
        conn.close()

    @staticmethod
    def get_autorole(guild_id: int): #Funçao para ver qual o Autorole definido
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
    
    @staticmethod
    def clear_autorole(guild_id: int): #Funçao de Reset de Autorole
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE settings
            SET autorole_id = NULL
            WHERE guild_id = ?
        """, (guild_id,))

        conn.commit()
        conn.close()

    @staticmethod
    def set_logs_channel(guild_id: int, channel_id: int): #Funçao escolha de canal de logs
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO settings (guild_id, logs_channel_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id)
            DO UPDATE SET logs_channel_id = excluded.logs_channel_id
        """, (guild_id, channel_id))

        conn.commit()
        conn.close()


    @staticmethod
    def get_logs_channel(guild_id: int):#Funçao de de verificaçao do canal de logs
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT logs_channel_id
            FROM settings
            WHERE guild_id = ?
        """, (guild_id,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]

        return None    
    