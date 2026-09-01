import mysql.connector
from mysql.connector import Error

from config import (
    DB_HOST,
    DB_PORT,
    DB_USER,
    DB_PASSWORD,
    DB_NAME
)


def get_connection():

    try:

        return mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

    except Error as e:

        print(f"❌ Erro ao ligar ao MySQL: {e}")

        raise


def initialize_database():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (

            guild_id BIGINT PRIMARY KEY,

            autorole_id BIGINT,

            logs_channel_id BIGINT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ticket_settings (

            id INT AUTO_INCREMENT PRIMARY KEY,

            guild_id BIGINT NOT NULL,

            ticket_type VARCHAR(100) NOT NULL,

            category_id BIGINT,

            staff_role_id BIGINT,

            UNIQUE(guild_id, ticket_type)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS whl_settings (

            id INT AUTO_INCREMENT PRIMARY KEY,

            guild_id BIGINT NOT NULL,

            whl_type VARCHAR(100) NOT NULL,

            category_id BIGINT,

            staff_role_id BIGINT,

            UNIQUE(guild_id, whl_type)
        )
    """)

    conn.commit()

    cursor.close()
    conn.close()