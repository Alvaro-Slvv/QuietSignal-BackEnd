import os
from sqlalchemy import inspect, text
from sqlalchemy.exc import ProgrammingError
from quietsignal_backend.database import engine, Base

# Define schema required for each table
# Add your tables + required columns here
REQUIRED_SCHEMAS = {
    "users": {
        "id": "INTEGER",
        "name": "VARCHAR(100)",
        "username": "VARCHAR(100)",
        "email": "VARCHAR(255)",
        "hashed_password": "VARCHAR(255)",
        "role": "VARCHAR(50)"
    }
}

def create_database_if_not_exists(engine):
    """For SQLite or file-based DBs — ensure the file exists."""
    url = str(engine.url)

    if url.startswith("sqlite:///"):
        db_file = url.replace("sqlite:///", "")
        if not os.path.exists(db_file):
            print(f"[DB INIT] Creating new SQLite database: {db_file}")
            open(db_file, "w").close()

def create_missing_tables(engine):
    """Creates tables that do not exist."""
    print("[DB INIT] Creating missing tables if necessary...")
    Base.metadata.create_all(engine)

def add_missing_columns(engine):
    """Detects missing columns and adds them (ALTER TABLE)."""

    inspector = inspect(engine)

    with engine.connect() as conn:
        for table_name, required_cols in REQUIRED_SCHEMAS.items():
            existing_cols = {col["name"] for col in inspector.get_columns(table_name)}

            for col_name, col_type in required_cols.items():
                if col_name not in existing_cols:
                    print(f"[DB INIT] Adding missing column {col_name} to {table_name}")

                    try:
                        conn.execute(
                            text(f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type};")
                        )
                    except ProgrammingError as e:
                        print(f"[DB INIT] ERROR adding column {col_name}: {e}")


def initialize_database():
    print("[DB INIT] Starting database initialization...")
    create_database_if_not_exists(engine)
    create_missing_tables(engine)
    add_missing_columns(engine)
    print("[DB INIT] Database initialization complete.")
