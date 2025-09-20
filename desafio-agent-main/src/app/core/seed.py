from sqlalchemy.orm import Session
from app.core.db import SessionLocal
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def seed_users(db: Session):
    if db.query(User).first():
        print("Usuários já existem, seed ignorado.")
        return

    user_data = UserCreate(
        name="Admin",
        email="admin@desafio.com",
        password="admin123"
    )

    user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )

    db.add(user)
    db.commit()
    print(f"Usuário seed criado: {user.email}")


def run():
    db = SessionLocal()
    try:
        seed_users(db)
    finally:
        db.close()


if __name__ == "__main__":
    run()