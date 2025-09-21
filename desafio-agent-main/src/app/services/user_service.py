from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.logging import get_logger

logger = get_logger(__name__)


class UserService:
    """
    Regras de negócio e persistência para Usuários.
    """

    def list_users(self, db: Session) -> list[User]:
        users = db.query(User).all()
        logger.info(f"Listando {len(users)} usuários")
        return users

    def get_user(self, db: Session, user_id: int) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def create_user(self, db: Session, user_in: UserCreate) -> User:
        user = User(name=user_in.name, email=user_in.email, password=user_in.password)
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"Usuário criado com sucesso: {user.id}")
        return user

    def update_user(self, db: Session, db_user: User, user_update: UserUpdate) -> User:
        for key, value in user_update.dict(exclude_unset=True).items():
            setattr(db_user, key, value)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Usuário {db_user.id} atualizado com sucesso")
        return db_user

    def delete_user(self, db: Session, db_user: User) -> None:
        db.delete(db_user)
        db.commit()
        logger.info(f"Usuário {db_user.id} deletado com sucesso")