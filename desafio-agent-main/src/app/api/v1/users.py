from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.services.user_service import UserService
from app.core.logging import get_logger

router = APIRouter(prefix="/users", tags=["Usuários"])
logger = get_logger(__name__)
user_service = UserService()


@router.get("/", response_model=list[UserRead], summary="Listar usuários")
def get_users(db: Session = Depends(get_db)):
    return user_service.list_users(db)


@router.get("/{user_id}", response_model=UserRead, summary="Consultar usuário por ID")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não foi encontrado.")
    return user


@router.post("/", response_model=UserRead, summary="Criar usuário")
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user_in)


@router.put("/{user_id}", response_model=UserRead, summary="Atualizar usuário")
def update_user(user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = user_service.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não foi encontrado.")
    return user_service.update_user(db, db_user, user_update)


@router.delete("/{user_id}", response_model=dict, summary="Deletar usuário")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não foi encontrado.")
    user_service.delete_user(db, db_user)
    return {"message": f"Usuário {user_id} deletado com sucesso!"}
