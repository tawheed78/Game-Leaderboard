import redis.asyncio as aioredis # type: ignore
from ..configs.redis.redis import get_redis_client


async def add_game_score_to_redis(sorted_set: str, score: dict):
    redis = await get_redis_client()
    await redis.zadd(sorted_set, {score.user_id: score.score})
    