from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.postgres_models import GameScoreModel, UserModel, GameModel
from ..schemas.postgres_schema import GameScoreCreate, GameScoreResponse
from ..configs.database.postgres_config import get_postgres_db

router = APIRouter()

@router.post("/scores", response_model=GameScoreResponse)
async def create_game_score(score: GameScoreCreate, db: Session = Depends(get_postgres_db)):
    try:
        if not db.query(UserModel).filter(UserModel.id == score.user_id).first():
            raise HTTPException(status_code=404, detail="User not found")
        if not db.query(GameModel).filter(GameModel.id == score.game_id).first():
            raise HTTPException(status_code=404, detail="Game not found")
        db_score = GameScoreModel(
            user_id=score.user_id,
            game_id=score.game_id,
            score=score.score,
            created_at=datetime.now()
        )
        db.add(db_score)
        db.commit()
        db.refresh(db_score)
        return db_score
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))