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

router = APIRouter()

@router.post("/games/{game_id}/join", response_model=GameSessionResponse)
async def create_game_session(game_id: int, user_id: int, db: Session = Depends(get_postgres_db), redis: aioredis.Redis = Depends(get_redis_client)):
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
        
        game_score = random.choice(range(0, 101, 5))
        db_game_Session = GameSessionModel(
            user_id=user_id,
            game_id=game_id,
            score=game_score,
            start_time=datetime.now()
        )
        game_activity_status.number_of_users_joined += 1
        db.add(db_game_Session)
        db.commit()
        db.refresh(db_game_Session)

        try:
            global_leaderboard = "global_leaderboard"
            game_leaderboard = f"game_{game_id}_leaderboard"
            await add_game_score_to_redis(global_leaderboard, user_id, game_score)
            await add_game_score_to_redis(game_leaderboard, user_id, game_score)
        except Exception as redis_error:
            raise HTTPException(status_code=500, detail=f"Redis error: {redis_error}")
        return db_game_Session
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    

@router.put("/games/{game_id}/exit", response_model=GameSessionResponse)
async def update_game_session(game_id: int, user_id: int, db: Session = Depends(get_postgres_db), redis: aioredis.Redis = Depends(get_redis_client)):
    try:
        game_session = db.query(GameSessionModel).filter(
            GameSessionModel.game_id == game_id,
            GameSessionModel.user_id == user_id,
            GameSessionModel.game_status == "STARTED"
        ).first()
        if not game_session:
            raise HTTPException(status_code=404, detail="Game session not found")
        game_session.end_time = datetime.now()
        game_session.game_status = "COMPLETED"
        db.commit()
        db.refresh(game_session)
        return game_session
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    