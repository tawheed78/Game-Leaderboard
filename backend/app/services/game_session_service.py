"""Service Module for Game Session"""

import random
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from ..utils.utils import add_game_score_to_redis
from ..models.postgres_models import GameSessionModel


async def create_game_session_service(user_id: int, game_id: int, game_activity_status, db):
    """Business Logic to Create a Game Session to upate the Game start, end time as well as number of users joined."""
    try:
        game_score = random.choice(range(0, 101, 5))
        
        db_game_Session = GameSessionModel(
            user_id=user_id,
            game_id=game_id,
            score=game_score,
            start_time=datetime.now()
        )
        game_activity_status.number_of_users_joined += 1
        db.add(db_game_Session)
        db.commit()
        db.refresh(db_game_Session)

        try:
            today_date = datetime.today().date()
            global_leaderboard = "global_leaderboard"
            game_leaderboard = f"game_{game_id}_leaderboard"
            global_leaderboard_date = f"global_leaderboard_{today_date}"
            game_leaderboard_date = f"game_{game_id}_leaderboard_{today_date}"
            await add_game_score_to_redis(global_leaderboard, user_id, game_score)
            await add_game_score_to_redis(game_leaderboard, user_id, game_score)
            await add_game_score_to_redis(global_leaderboard_date, user_id, game_score)
            await add_game_score_to_redis(game_leaderboard_date, user_id, game_score)
        except Exception as redis_error:
            raise HTTPException(status_code=500, detail=f"Redis error: {redis_error}")
        return db_game_Session
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
async def update_game_session_service(game_session, db):
    """Business Logic to Update the Game session with the End time and status"""
    try:
        game_session.end_time = datetime.now()
        game_session.game_status = "COMPLETED"
        db.commit()
        db.refresh(game_session)
        return game_session
    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    