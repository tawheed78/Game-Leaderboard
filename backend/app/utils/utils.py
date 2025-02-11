import asyncio
import calendar

from fastapi import HTTPException

from ..services.game_service import popularity_index_service
from ..models.postgres_models import GameModel, GameSessionModel
from ..configs.database.postgres_config import SessionLocal
import redis.asyncio as aioredis # type: ignore
from datetime import datetime, timedelta
from ..configs.redis.redis import get_redis_client


async def has_played_today(user_id, game_id, db):
    try:
        today_start = datetime.now().date()
        today_end = today_start + timedelta(days=1)
        todays_session = db.query(GameSessionModel).filter(
            GameSessionModel.user_id == user_id,
            GameSessionModel.game_id == game_id,
            GameSessionModel.start_time >= today_start,
            GameSessionModel.start_time <= today_end
        ).first()
        if todays_session:
            return True
        else:
            return False
    except Exception as redis_error:
        raise HTTPException(status_code=500, detail=f"Redis error: {redis_error}")    


async def get_game_popularity_index():
    db = SessionLocal()
    redis = await get_redis_client()
    try:
        yesterday_start = datetime.now().date() - timedelta(days=1)
        yesterday_end = yesterday_start + timedelta(days=1)
        
        game_ids = [game.id for game in db.query(GameModel.id).all()]
        cache_key = "popularity_index"
        tasks = [
            popularity_index_service(game_id, yesterday_start, yesterday_end, db)
            for game_id in game_ids
        ]
        popularity_list = await asyncio.gather(*tasks)

        async with redis.pipeline() as pipe:
            pipe.delete(cache_key)
            for item in popularity_list:
                game_id = item.get('game_id')
                score = item.get("popularity_index")
                pipe.zadd(cache_key, {str(game_id):float(score)})
            await pipe.execute()
        print("🔄 Popularity index updated for all games!")
    except Exception as e:
        print(f"⚠️ Error in popularity index update: {str(e)}")
    finally:
        db.close()


async def add_game_score_to_redis(sorted_set: str, user_id: int, score: int):
    redis = await get_redis_client()
    await redis.zincrby(sorted_set, score, user_id)
    ttl = await redis.ttl(sorted_set)
    if ttl == -1:
        await redis.expireat(sorted_set, get_end_of_month_timestamp())


def get_end_of_month_timestamp():
    now = datetime.now()
    last_day = calendar.monthrange(now.year, now.month)[1]
    end_of_month = datetime(now.year, now.month, last_day, 23, 59, 59)
    return int(end_of_month.timestamp())