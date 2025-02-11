
import redis.asyncio as aioredis # type: ignore
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.postgres_models import GameModel, GameStatusModel
from ..schemas.postgres_schema import GameCreate, GameResponse, GameStatusResponse
from ..services.game_service import create_game_service, start_game_service, end_game_service, upvote_game_service
from ..configs.database.postgres_config import get_postgres_db
from ..configs.redis.redis import get_redis_client
from apscheduler.schedulers.asyncio import AsyncIOScheduler # type: ignore
from ..utils.utils import get_game_popularity_index

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

# scheduler = AsyncIOScheduler()
# scheduler.add_job(get_game_popularity_index, "interval", minutes=1)
# scheduler.start()