from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.postgres_models import GameModel
from ..schemas.postgres_schema import GameCreate, GameResponse
from ..configs.database.postgres_config import get_postgres_db

router = APIRouter()

@router.post("/games", response_model=GameResponse)
async def create_game(game: GameCreate, db: Session = Depends(get_postgres_db)):
    try:
        db_game = GameModel(
            title=game.title,
            description=game.description,
            created_at=datetime.now()
        )
        db.add(db_game)
        db.commit()
        db.refresh(db_game)
        return db_game
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/games/{game_id}/upvote", response_model=GameResponse)
async def upvote_game(game_id: int, db: Session = Depends(get_postgres_db)):
    try:
        game = db.query(GameModel).filter(GameModel.id == game_id).first()
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        game.upvotes += 1
        db.commit()
        db.refresh(game)
        return game
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))