import mysql.connector
from sqlalchemy import create_engine
from quietsignal_backend.settings import settings


def ensure_database_exists():
    """
    Ensures the MySQL database exists BEFORE SQLAlchemy connects.
    """
    conn = mysql.connector.connect(
        host=settings.MYSQL_HOST,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.MYSQL_DB}")
    conn.commit()
    cursor.close()
    conn.close()


# Ensure DB before SQLAlchemy connects
ensure_database_exists()

# SQLAlchemy Engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
)
