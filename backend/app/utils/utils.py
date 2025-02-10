import calendar
import redis.asyncio as aioredis # type: ignore
from datetime import datetime, timedelta
from ..configs.redis.redis import get_redis_client


async def add_game_score_to_redis(sorted_set: str, user_id: int, score: int):
    redis = await get_redis_client()
    await redis.zincrby(sorted_set, score, user_id)


def get_end_of_month_timestamp():
    now = datetime.now()
    last_day = calendar.monthrange(now.year, now.month)[1]  # Get last day of the current month
    end_of_month = datetime(now.year, now.month, last_day, 23, 59, 59)  # Last second of the month
    return int(end_of_month.timestamp())