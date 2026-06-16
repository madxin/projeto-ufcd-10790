from database.database import get_connection


class TicketSettingsDAL:

    @staticmethod
    def set_ticket_category(
        guild_id,
        ticket_type,
        category_id
    ):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ticket_settings
            (guild_id, ticket_type, category_id)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, ticket_type)
            DO UPDATE SET
                category_id = excluded.category_id
        """, (
            guild_id,
            ticket_type.lower(),
            category_id
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def set_ticket_role(
        guild_id,
        ticket_type,
        staff_role_id
    ):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ticket_settings
            (guild_id, ticket_type, staff_role_id)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id, ticket_type)
            DO UPDATE SET
                staff_role_id = excluded.staff_role_id
        """, (
            guild_id,
            ticket_type.lower(),
            staff_role_id
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def get_ticket_config(
        guild_id,
        ticket_type
    ):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT category_id, staff_role_id
            FROM ticket_settings
            WHERE guild_id = ? AND ticket_type = ?
        """, (
            guild_id,
            ticket_type.lower()
        ))

        result = cursor.fetchone()

        conn.close()

        return result

    @staticmethod
    def get_all_ticket_configs(
        guild_id
    ):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                ticket_type,
                category_id,
                staff_role_id
            FROM ticket_settings
            WHERE guild_id = ?
            ORDER BY ticket_type
        """, (guild_id,))

        result = cursor.fetchall()

        conn.close()

        return result