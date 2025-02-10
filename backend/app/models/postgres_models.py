"Model Configuration Module for Postgres DB"
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from ..configs.database.postgres_config import Base

class GameStatus(Enum):
    STARTED = "STARTED"
    COMPLETED = "COMPLETED"

class UserModel(Base):
    "User Model Class"
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    game_session = relationship("GameSessionModel", back_populates="users")


class GameModel(Base):
    "Game Model Class"
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String, unique=True, index=True)
    description = Column(String)
    upvotes = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    game_session = relationship("GameSessionModel", back_populates="games")

class GameSessionModel(Base):
    "Game Score Model Class"
    __tablename__ = "game_session"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    game_id = Column(Integer, ForeignKey('games.id'))
    start_time = Column(DateTime, default=datetime.now)
    end_time = Column(DateTime)
    game_status = Column(String, default=GameStatus.STARTED.value)
    score = Column(Integer)

    users = relationship("UserModel", back_populates="game_session")
    games = relationship("GameModel", back_populates="game_session")