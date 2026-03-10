import oracledb
import os

def get_connection():

    user = os.environ.get("DB_USER")
    password = os.environ.get("DB_PASSWORD")
    dsn = os.environ.get("DB_DSN")

    connection = oracledb.connect(
        user=user,
        password=password,
        dsn=dsn
    )

    return connection