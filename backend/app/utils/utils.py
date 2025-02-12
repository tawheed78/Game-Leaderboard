import asyncio, calendar

from datetime import datetime, timedelta
from fastapi import HTTPException

from ..services.game_service import popularity_index_service
from ..models.postgres_models import GameModel
from ..configs.database.postgres_config import SessionLocal
from ..configs.redis.redis import get_redis_client    


async def get_game_popularity_index():
    """Business logic to Update the Popularity Index"""
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
    """Business Logic to Add score to Redis Sorted Sets"""
    redis = await get_redis_client()
    await redis.zincrby(sorted_set, score, user_id)
    ttl = await redis.ttl(sorted_set)
    if ttl == -1:
        await redis.expireat(sorted_set, get_end_of_month_timestamp())


def get_end_of_month_timestamp():
    """Business Logic to Fetch end of month timestamp"""
    now = datetime.now()
    last_day = calendar.monthrange(now.year, now.month)[1]
    end_of_month = datetime(now.year, now.month, last_day, 23, 59, 59)
    return int(end_of_month.timestamp())