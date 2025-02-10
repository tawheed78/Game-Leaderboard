import redis.asyncio as aioredis # type: ignore

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.postgres_models import GameSessionModel, UserModel, GameModel
from ..schemas.postgres_schema import GameSessionResponse, GameSessionCreate
from ..configs.database.postgres_config import get_postgres_db
from ..configs.redis.redis import get_redis_client
from ..utils.utils import add_game_score_to_redis

router = APIRouter()

@router.post("/scores", response_model=GameSessionResponse)
async def create_game_session(session: GameSessionCreate, db: Session = Depends(get_postgres_db), redis: aioredis.Redis = Depends(get_redis_client)):
    try:
        if not db.query(UserModel).filter(UserModel.id == session.user_id).first():
            raise HTTPException(status_code=404, detail="User not found")
        if not db.query(GameModel).filter(GameModel.id == session.game_id).first():
            raise HTTPException(status_code=404, detail="Game not found")
        global_leaderboard = "global_leaderboard"
        game_leaderboard = f"game_{session.game_id}_leaderboard"
        db_score = GameSessionModel(
            user_id=session.user_id,
            game_id=session.game_id,
            score=session.score,
            start_time=datetime.now()
        )
        db.add(db_score)
        db.commit()
        db.refresh(db_score)
        await add_game_score_to_redis(global_leaderboard, session.user_id, session.score)
        await add_game_score_to_redis(game_leaderboard, session.user_id, session.score)
        return db_score
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.put("/scores/{game_session_id}", response_model=GameSessionResponse)
async def update_game_session(game_session_id: int, db: Session = Depends(get_postgres_db), redis: aioredis.Redis = Depends(get_redis_client)):
    try:
        game_session = db.query(GameSessionModel).filter(GameSessionModel.id == game_session_id).first()
        if not game_session:
            raise HTTPException(status_code=404, detail="Game session not found")
        game_session.end_time = datetime.now()
        game_session.game_status = "COMPLETED"
        db.commit()
        db.refresh(game_session)
        return game_session
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    