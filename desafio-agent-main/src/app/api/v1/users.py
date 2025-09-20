from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.core.logging import get_logger

router = APIRouter(prefix="/users", tags=["users"])
logger = get_logger(__name__)

# GET all users
@router.get("/", response_model=list[UserRead])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    logger.info(f"Listando {len(users)} usuários")
    return users

# GET user by ID
@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        logger.warning(f"Usuário {user_id} não encontrado")
        raise HTTPException(status_code=404, detail="Usuário não foi encontrado.")
    logger.info(f"Usuário {user_id} consultado com sucesso")
    return user

# POST create user
@router.post("/", response_model=UserRead)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Criando usuário: {user_in.name}, email: {user_in.email}")
    user = User(name=user_in.name, email=user_in.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"Usuário criado com sucesso: ID {user.id}")
    return user

# Update user
@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.warning(f"Usuário {user_id} não encontrado para atualização")
        raise HTTPException(status_code=404, detail="Usuário não foi encontrado.")
    
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    logger.info(f"Usuário {user_id} atualizado com sucesso")
    return db_user

# Delete user
@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        logger.warning(f"Usuário {user_id} não encontrado para deleção")
        raise HTTPException(status_code=404, detail="Usuário não foi encontrado.")
    
    db.delete(db_user)
    db.commit()
    logger.info(f"Usuário {user_id} deletado com sucesso")
    return {"message": f"Usuário {user_id} deletado com sucesso!"}