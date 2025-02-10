from typing import List
import redis.asyncio as aioredis # type: ignore

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..schemas.postgres_schema import LeaderboardResponse
from ..configs.redis.redis import get_redis_client
from ..configs.database.postgres_config import get_postgres_db
from ..models.postgres_models import GameModel

router = APIRouter()

@router.get("/leaderboard/global", response_model=List[LeaderboardResponse])
async def get_global_leaderboard(redis: aioredis.Redis = Depends(get_redis_client)):
    try:
        global_leaderboard = "global_leaderboard"
        leaderboard_data = await redis.zrevrange(global_leaderboard, 0, 9, withscores=True)
        # await redis.zrem(global_leaderboard, "4")
        leaderboard = [{"user_id": user, "score": score} for user, score in leaderboard_data]
        return leaderboard
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/leaderboard/{game_id}", response_model=List[LeaderboardResponse])
async def get_game_leaderboard(game_id: int, db: Session = Depends(get_postgres_db), redis: aioredis.Redis = Depends(get_redis_client)):
    try:
        game = db.query(GameModel).filter(GameModel.id == game_id).first()
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        game_leaderboard = f"game_{game_id}_leaderboard"
        # await redis.zrem(game_leaderboard, "40")
        leaderboard_data = await redis.zrevrange(game_leaderboard, 0, 50, withscores=True)
        leaderboard = [{"user_id": user, "score": score} for user, score in leaderboard_data]
        return leaderboard
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))