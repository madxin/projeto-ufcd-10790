from src.database.database import get_connection


class WhlSettingsDAL:

    @staticmethod
    def set_whl_category(
        guild_id,
        whl_type,
        category_id
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO whl_settings (
                guild_id,
                whl_type,
                category_id
            )
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                category_id = VALUES(category_id)
        """, (
            guild_id,
            whl_type.lower(),
            category_id
        ))

        conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def set_whl_role(
        guild_id,
        whl_type,
        staff_role_id
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO whl_settings (
                guild_id,
                whl_type,
                staff_role_id
            )
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                staff_role_id = VALUES(staff_role_id)
        """, (
            guild_id,
            whl_type.lower(),
            staff_role_id
        ))

        conn.commit()

        cursor.close()
        conn.close()

    @staticmethod
    def get_whl_config(
        guild_id,
        whl_type
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                category_id,
                staff_role_id
            FROM whl_settings
            WHERE guild_id = %s
            AND whl_type = %s
        """, (
            guild_id,
            whl_type.lower()
        ))

        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result

    @staticmethod
    def get_all_whl_configs(
        guild_id
    ):

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                whl_type,
                category_id,
                staff_role_id
            FROM whl_settings
            WHERE guild_id = %s
            ORDER BY whl_type
        """, (
            guild_id,
        ))

        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result