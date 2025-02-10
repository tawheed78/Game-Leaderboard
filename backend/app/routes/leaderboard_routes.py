from typing import List
import redis.asyncio as aioredis # type: ignore

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from redis.exceptions import RedisError # type: ignore

from ..schemas.postgres_schema import LeaderboardResponse
from ..configs.redis.redis import get_redis_client
from ..configs.database.postgres_config import get_postgres_db
from ..models.postgres_models import GameModel
from ..services.leaderboard_service import global_leaderboard_service, game_leaderboard_service
router = APIRouter()

@router.get("/leaderboard/global", response_model=List[LeaderboardResponse])
async def get_global_leaderboard(redis: aioredis.Redis = Depends(get_redis_client)):
    global_leaderboard = "global_leaderboard"
    response = await global_leaderboard_service(global_leaderboard, redis)
    return response
    
@router.get("/leaderboard/{game_id}", response_model=List[LeaderboardResponse])
async def get_game_leaderboard(game_id: int, db: Session = Depends(get_postgres_db), redis: aioredis.Redis = Depends(get_redis_client)):
    game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    game_leaderboard = f"game_{game_id}_leaderboard"
    response = await game_leaderboard_service(game_leaderboard, redis)
    return response