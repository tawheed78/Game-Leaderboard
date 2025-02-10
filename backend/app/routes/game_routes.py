from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from ..models.postgres_models import GameModel, GameSessionModel, GameStatusModel, UserModel
from ..schemas.postgres_schema import GameCreate, GameResponse, GameStatusResponse
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
    
@router.post("/games/{game_id}/start", response_model=GameStatusResponse)
async def start_game(game_id: int, db: Session = Depends(get_postgres_db)):
    try:
        game = db.query(GameModel).filter(GameModel.id == game_id).first()
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        game_is_active = db.query(GameStatusModel).filter(
            GameStatusModel.game_id == game_id,
            GameStatusModel.status == "STARTED"
        ).first()
        if game_is_active:
            raise HTTPException(status_code=404, detail="Game has started already.")
        db_game = GameStatusModel(
            game_id = game_id
        )
        db.add(db_game)
        db.commit()
        db.refresh(db_game)
        
        return db_game
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/games/{game_id}/end", response_model=GameStatusResponse)
async def end_game(game_id: int, db: Session = Depends(get_postgres_db)):
    try:
        game = db.query(GameModel).filter(GameModel.id == game_id).first()
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        db_game = db.query(GameStatusModel).filter(GameStatusModel.game_id == game_id, GameStatusModel.status == "STARTED").first()
        if not db_game:
            raise HTTPException(status_code=404, detail="The game has ended.")
        db_game.status = "ENDED"
        db_game.ended_at = datetime.now()
        db.commit()
        db.refresh(db_game)
        return db_game
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# @router.post("games/{game_id}/join")
# async def join_game(game_id: int, user_id: int, db: Session = Depends(get_postgres_db)):
#     try:
#         game = db.query(GameModel).filter(GameModel.id == game_id).first()
#         if not game:
#             raise HTTPException(status_code=404, detail="Game not found")
#         user = db.query(UserModel).filter(UserModel.id == user_id).first()
#         if not user:
#             raise HTTPException(status_code=404, detail="User not found")
        

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
    

@router.get("/games/{game_id}/popularity-index")
async def get_popularity_index(game_id: int, db: Session = Depends(get_postgres_db)):
    try:
        yesterday_start = datetime.now().date() - timedelta(days=1)
        yesterday_end = yesterday_start + timedelta(days=1)
        
        game = db.query(GameModel).filter(GameModel.id == game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Game not found")
        
        w1 = db.query(GameSessionModel.user_id).filter(
            GameSessionModel.game_id == game_id, 
            GameSessionModel.start_time >= yesterday_start,
            GameSessionModel.start_time < yesterday_end
        ).distinct().count()
        
        w2 = db.query(GameSessionModel).filter(
            GameSessionModel.game_id == game_id,
            GameSessionModel.game_status == "STARTED"
        ).count()
        
        w3 = db.query(GameModel).filter(GameModel.id == game_id).first().upvotes
        
        w4_query = (db.query(func.max(GameSessionModel.end_time - GameSessionModel.start_time))
        .filter(
            GameSessionModel.game_id == game_id,
            GameSessionModel.start_time >= yesterday_start,  
            GameSessionModel.end_time < yesterday_end,
            GameSessionModel.end_time.isnot(None)
        ).scalar())
        w4 = w4_query.total_seconds() if w4_query else 0

        w5 = (db.query(GameSessionModel.end_time - GameSessionModel.start_time)
        .filter(
            GameSessionModel.game_id == game_id,
            GameSessionModel.start_time >= yesterday_start,
            GameSessionModel.end_time < yesterday_end,
            GameSessionModel.end_time.isnot(None)
        ).count())
        
        max_daily_players = db.query(GameSessionModel.user_id).filter( 
            GameSessionModel.start_time >= yesterday_start,
            GameSessionModel.start_time < yesterday_end
        ).distinct().count() or 1
        
        max_concurrent_players = db.query(GameSessionModel).filter(
            GameSessionModel.game_status == "STARTED"
        ).distinct().count() or 1
        
        max_upvotes = db.query(func.max(GameModel.upvotes)).scalar() or 1
        
        max_session_length_hours = (db.query(func.max(GameSessionModel.end_time - GameSessionModel.start_time))
        .filter(
            GameSessionModel.start_time >= yesterday_start,  
            GameSessionModel.end_time < yesterday_end,
            GameSessionModel.end_time.isnot(None)
        ).scalar())
        max_session_length = max_session_length_hours.total_seconds() if max_session_length_hours else 1

        max_daily_sessions = (db.query(GameSessionModel.end_time - GameSessionModel.start_time)
        .filter(
            GameSessionModel.start_time >= yesterday_start,
            GameSessionModel.end_time < yesterday_end,
            GameSessionModel.end_time.isnot(None)
        ).count()) or 1
        
        popularity_index =  (0.3 * (w1/max_daily_players) + 
         0.2 * (w2/max_concurrent_players) + 
         0.25 * (w3/max_upvotes) + 
         0.15 * (w4/max_session_length) + 
         0.1 * (w5/max_daily_sessions))

        return {"game_id": game_id, "popularity_index": round(popularity_index, 2)}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))