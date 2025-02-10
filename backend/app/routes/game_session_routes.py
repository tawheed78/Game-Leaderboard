import random
import redis.asyncio as aioredis # type: ignore

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.postgres_models import GameSessionModel, UserModel, GameModel, GameStatusModel
from ..schemas.postgres_schema import GameSessionResponse
from ..configs.database.postgres_config import get_postgres_db
from ..configs.redis.redis import get_redis_client
from ..utils.utils import add_game_score_to_redis, get_end_of_month_timestamp
from ..services.game_session_service import create_game_session_service, update_game_session_service

router = APIRouter()

@router.post("/games/{game_id}/join", response_model=GameSessionResponse)
async def join_game(game_id: int, user_id: int, db: Session = Depends(get_postgres_db), redis: aioredis.Redis = Depends(get_redis_client)):
    try:
        if not db.query(UserModel).filter(UserModel.id == user_id).first():
            raise HTTPException(status_code=404, detail="User not found")
        if not db.query(GameModel).filter(GameModel.id == game_id).first():
            raise HTTPException(status_code=404, detail="Game not found")
        
        game_activity_status = db.query(GameStatusModel).filter(
            GameStatusModel.game_id == game_id,
            GameStatusModel.status == "STARTED").first()
        if not game_activity_status:
            raise HTTPException(status_code=404, detail="Game has ended.")
        
        if db.query(GameSessionModel).filter(
            GameSessionModel.game_id == game_id,
            GameSessionModel.user_id == user_id,
            GameSessionModel.game_status == "STARTED"
        ).first():
            raise HTTPException(status_code=404, detail="An active game session exists. Please go back to the game or end the previous game session to start a new one.")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    response = await create_game_session_service(user_id, game_id, game_activity_status, db)
    return response
    

@router.put("/games/{game_id}/exit", response_model=GameSessionResponse)
async def exit_game(game_id: int, user_id: int, db: Session = Depends(get_postgres_db), redis: aioredis.Redis = Depends(get_redis_client)):
    try:
        game_session = db.query(GameSessionModel).filter(
            GameSessionModel.game_id == game_id,
            GameSessionModel.user_id == user_id,
            GameSessionModel.game_status == "STARTED"
        ).first()
        if not game_session:
            raise HTTPException(status_code=404, detail="Game session not found")
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    response = await update_game_session_service(game_session, db)
    return response
    