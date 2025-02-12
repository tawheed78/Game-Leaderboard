"""Service Module for Game Routes"""

from datetime import datetime
from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from ..models.postgres_models import GameModel, GameSessionModel, GameStatusModel
from ..schemas.postgres_schema import GameCreate


async def create_game_service(game: GameCreate, db):
    """Business Logic to Create a New Game"""
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
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
async def start_game_service(game_id: int, db):
    """Business Logic to Start a Game"""
    try:
        db_game = GameStatusModel(
            game_id = game_id
        )
        db.add(db_game)
        db.commit()
        db.refresh(db_game)
        return db_game
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
async def end_game_service(db_game, db):
    """Business Logic to End a Game"""
    try:
        db_game.status = "ENDED"
        db_game.ended_at = datetime.now()
        db.commit()
        db.refresh(db_game)
        return db_game
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
async def upvote_game_service(game, db):
    """Business Logic to Upvote a Game"""
    try:
        game.upvotes += 1
        db.commit()
        db.refresh(game)
        return game
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Unexpected error: " + str(e))
    
async def popularity_index_service(game_id, yesterday_start, yesterday_end, db):
    """Business Logic to fetch the Popularity Index"""
    try:
        # w1 - Number of players who played the Game Yesterday
        # w2 - Number of people playing the game right now
        # w3 - Total number of upvotes received for the game
        # w4 - Maximum session length of the game played (considering only the sessions played yesterday)
        # w5 - Total number of sessions played yesterday

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
    