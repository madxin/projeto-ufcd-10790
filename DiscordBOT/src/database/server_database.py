import mysql.connector

from config import (
    SERVER_DB_HOST,
    SERVER_DB_PORT,
    SERVER_DB_USER,
    SERVER_DB_PASSWORD,
    SERVER_DB_NAME
)


def get_server_connection():
    return mysql.connector.connect(
        host=SERVER_DB_HOST,
        port=SERVER_DB_PORT,
        user=SERVER_DB_USER,
        password=SERVER_DB_PASSWORD,
        database=SERVER_DB_NAME
    )