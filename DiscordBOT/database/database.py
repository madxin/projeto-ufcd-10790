import sqlite3
from pathlib import Path

# Caminho para a base de dados
DB_PATH = Path(__file__).resolve().parent.parent / "database.db"


def get_connection():
    """Cria e devolve uma ligação à base de dados."""
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Cria as tabelas necessárias caso não existam."""

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            guild_id INTEGER PRIMARY KEY,
            autorole_id INTEGER,
            logs_channel_id INTEGER
        )
    """)

    conn.commit()
    conn.close()