"""Service Module for User Operations"""

from datetime import datetime
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from ..schemas.postgres_schema import UserCreate, UserUpdate
from ..models.postgres_models import UserModel


async def user_create_service(user: UserCreate, db):
    """Business Logic to Create a New User"""
    try:
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
        return JSONResponse(status_code=400,content=f"Database Error: {str(e)}")
    except Exception as e:
        return JSONResponse(status_code=500, content=f"Unexpected Error: {str(e)}")


async def user_update_service(db_user, user: UserUpdate, db):
    """Business Logic to Update a User"""
    try:
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(e)}")
    

async def user_delete_service(db_user, db):
    """Business Logic to Delete a User"""
    try:
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected Error: {str(e)}")