import asyncio
import redis.asyncio as aioredis # type: ignore
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler # type: ignore
from ..models.postgres_models import GameModel, GameStatusModel
from ..schemas.postgres_schema import GameCreate, GameResponse, GameStatusResponse
from ..services.game_service import create_game_service, start_game_service, end_game_service, upvote_game_service, popularity_index_service
from ..configs.database.postgres_config import SessionLocal, get_postgres_db
from ..configs.redis.redis import get_redis_client

router = APIRouter()


@router.post("/games", response_model=GameResponse)
async def create_game(game: GameCreate, db: Session = Depends(get_postgres_db)):
    response = await create_game_service(game, db)
    return response
    

@router.post("/games/{game_id}/start", response_model=GameStatusResponse)
async def start_game(game_id: int, db: Session = Depends(get_postgres_db)):
    game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    game_is_active = db.query(GameStatusModel).filter(
        GameStatusModel.game_id == game_id,
        GameStatusModel.status == "STARTED"
    ).first()
    if game_is_active:
        raise HTTPException(status_code=404, detail="Game has started already.")
    response = await start_game_service(game_id, db)
    return response


@router.post("/games/{game_id}/end", response_model=GameStatusResponse)
async def end_game(game_id: int, db: Session = Depends(get_postgres_db)): 
    game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    db_game = db.query(GameStatusModel).filter(GameStatusModel.game_id == game_id, GameStatusModel.status == "STARTED").first()
    if not db_game:
        raise HTTPException(status_code=404, detail="The game has not started yet.")
    response = await end_game_service(db_game, db)
    return response


@router.post("/games/{game_id}/upvote", response_model=GameResponse)
async def upvote_game(game_id: int, db: Session = Depends(get_postgres_db)):
    game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    response = await upvote_game_service(game, db)
    return response


@router.get("/games/popularity-index")
async def popularity_index(redis: aioredis.Redis = Depends(get_redis_client)):
    popularity_index_key = "popularity_index"
    popularity_index_data = await redis.zrevrange(popularity_index_key, 0, 9, withscores=True)
    if popularity_index_data:
        return popularity_index_data
    raise HTTPException(status_code=404, detail="Popularity index not available yet. Try again in a few minutes.")


# async def get_game_popularity_index():
#     db = SessionLocal()
#     redis = await get_redis_client()
#     try:
#         yesterday_start = datetime.now().date() - timedelta(days=1)
#         yesterday_end = yesterday_start + timedelta(days=1)
        
#         game_ids = [game.id for game in db.query(GameModel.id).all()]
#         cache_key = "popularity_index"
#         tasks = [
#             popularity_index_service(game_id, yesterday_start, yesterday_end, db)
#             for game_id in game_ids
#         ]
#         popularity_list = await asyncio.gather(*tasks)

#         async with redis.pipeline() as pipe:
#             pipe.delete(cache_key)
#             for item in popularity_list:
#                 game_id = item.get('game_id')
#                 score = item.get("popularity_index")
#                 pipe.zadd(cache_key, {str(game_id):float(score)})
#             await pipe.execute()
#         print("🔄 Popularity index updated for all games!")
#     except Exception as e:
#         print(f"⚠️ Error in popularity index update: {str(e)}")
#     finally:
#         db.close()

# scheduler = AsyncIOScheduler()
# scheduler.add_job(get_game_popularity_index, "interval", minutes=5)
# scheduler.start()