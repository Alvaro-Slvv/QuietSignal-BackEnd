from sqlalchemy.orm import Session
from quietsignal_backend.database.base import SessionLocal, Base
from quietsignal_backend.database.engine import engine
from quietsignal_backend.settings import settings
from quietsignal_backend.utils.security import hash_password
from quietsignal_backend.models.dao.userDAO import UserDAO
from quietsignal_backend.models.dto.userDTO import UserCreateDTO


def initialize_database():
    """
    Creates tables and ensures admin user exists.
    Called ONCE during FastAPI lifespan startup.
    """
    print("[dbInitializer] Running initial setup...")

    # Create tables
    Base.metadata.create_all(bind=engine)
    print("[dbInitializer] Tables ensured")

    # Ensure admin user
    ensure_admin_user()
    print("[dbInitializer] Initialization complete")


def ensure_admin_user():
    db: Session = SessionLocal()
    try:
        existing = UserDAO.get_by_email(db, settings.ADMIN_EMAIL)
        if existing:
            print(f"[dbInitializer] Admin already exists: {settings.ADMIN_EMAIL}")
            return

        print(f"[dbInitializer] Creating admin user: {settings.ADMIN_EMAIL}")
        dto = UserCreateDTO(
            name=settings.ADMIN_NAME,
            username=settings.ADMIN_NAME,
            email=settings.ADMIN_EMAIL,
            password=settings.ADMIN_PASSWORD
        )

        hashed_pw = hash_password(dto.password)

        # ✔ create admin with role="admin"
        UserDAO.create(db, dto, hashed_pw, role="admin")
        db.commit()

        print(f"[dbInitializer] Admin user created: {settings.ADMIN_EMAIL}")

    except Exception as e:
        print("[dbInitializer] ERROR creating admin user:", e)
        db.rollback()
        raise  # Fail startup if admin creation fails
    finally:
        db.close()