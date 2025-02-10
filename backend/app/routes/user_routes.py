from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..models.postgres_models import UserModel
from ..schemas.postgres_schema import UserCreate, UserUpdate, User
from ..configs.database.postgres_config import get_postgres_db
from ..services.user_service import user_create_service, user_update_service, user_delete_service

router = APIRouter()

@router.post("/users", response_model=User)
async def create_user(user: UserCreate, db: Session = Depends(get_postgres_db)):
    existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    response = await user_create_service(user, db)
    return response
    

@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_postgres_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    response = await user_update_service(db_user, user, db)
    return response
    

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_postgres_db)):
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    response = await user_delete_service(db_user, db)
    return response