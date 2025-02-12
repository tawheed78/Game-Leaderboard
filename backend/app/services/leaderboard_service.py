"""Service Module for Leaderboard Routes"""

from fastapi import HTTPException
from redis.exceptions import RedisError # type: ignore
from sqlalchemy.exc import SQLAlchemyError

async def global_leaderboard_service(key, redis):
    """Business Logic to Fetch Global Leaderboard"""
    try:
        global_leaderboard = key
        leaderboard_data = await redis.zrevrange(global_leaderboard, 0, 9, withscores=True)
        if not leaderboard_data:
            raise HTTPException(status_code=404, detail="No global leaderboard data found")
        leaderboard = [{"user_id": user, "score": score} for user, score in leaderboard_data]
        return leaderboard
    except RedisError as e:
        raise HTTPException(status_code=500, detail="Redis error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    

async def game_leaderboard_service(key, redis):
    """Business Logic to fetch Game Leaderboard"""
    try:
        game_leaderboard = key
        leaderboard_data = await redis.zrevrange(game_leaderboard, 0, 50, withscores=True)
        if not leaderboard_data:
            raise HTTPException(status_code=404, detail="No leaderboard data found for this game")
        leaderboard = [{"user_id": user, "score": score} for user, score in leaderboard_data]
        return leaderboard
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error: " + str(e))
    except RedisError as e:
        raise HTTPException(status_code=500, detail="Redis error: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))