from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.postgres_models import GameModel, GameSessionModel, GameStatusModel, UserModel
from ..schemas.postgres_schema import GameCreate, GameResponse, GameStatusResponse
from ..services.game_service import create_game_service, start_game_service, end_game_service, upvote_game_service, popularity_index_service
from ..configs.database.postgres_config import get_postgres_db

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


@router.get("/games/{game_id}/popularity-index")
async def get_popularity_index(game_id: int, db: Session = Depends(get_postgres_db)):
    yesterday_start = datetime.now().date() - timedelta(days=1)
    yesterday_end = yesterday_start + timedelta(days=1)
    
    game = db.query(GameModel).filter(GameModel.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    response = await popularity_index_service(game_id, yesterday_start, yesterday_end, db)
    return response