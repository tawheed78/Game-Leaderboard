from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.postgres_models import UserModel
from ..schemas.postgres_schema import UserCreate, UserUpdate, User
from ..configs.database.postgres_config import get_postgres_db

router = APIRouter()

@router.post("/users", response_model=User)
async def create_user(user: UserCreate, db: Session = Depends(get_postgres_db)):
    try:
        existing_user = db.query(UserModel).filter(UserModel.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        db_user = UserModel(
            username=user.username,
            email=user.email,
            password=user.password,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database Error: {str(e)}")
    

@router.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_postgres_db)):
    try:
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        db_user.username = user.username or db_user.username
        db_user.email = user.email or db_user.email
        db_user.password = user.password or db_user.password
        db_user.updated_at = datetime.now()
        db.commit()
        db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database Error: {str(e)}")
    
@router.delete("users/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_postgres_db)):
    try:
        db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
        if db_user is None:
            raise HTTPException(status_code=404, detail="User not found")
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database Error: {str(e)}")