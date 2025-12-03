from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from ..config import settings

DATABASE_URL = settings.DATABASE_URL   # "mysql+mysqlconnector://user:pass@localhost:3306/quietsignal"

# Parse DSN
url = make_url(DATABASE_URL)

# Build server URL WITHOUT database
server_url = (
    f"{url.drivername}://{url.username}:{url.password}@{url.host}:{url.port}/"
)

# Create engine WITHOUT database (server-level)
server_engine = create_engine(server_url, isolation_level="AUTOCOMMIT")


def ensure_database():
    db_name = url.database

    with server_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{db_name}`"))


# Create DB before regular engine is made
ensure_database()

# Now the real engine WITH the database
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
