import redis.asyncio as aioredis # type: ignore
from ..configs.redis.redis import get_redis_client


async def add_game_score_to_redis(sorted_set: str, user_id: int, score: int):
    redis = await get_redis_client()
    await redis.zincrby(sorted_set, score, user_id)
    