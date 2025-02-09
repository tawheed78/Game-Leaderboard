"Model Configuration Module for Postgres DB"

from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from ..configs.database.postgres_config import Base

class UserModel(Base):
    "User Model Class"
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    game_scores = relationship("GameScoreModel", back_populates="users")


class GameModel(Base):
    "Game Model Class"
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String, unique=True, index=True)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    game_scores = relationship("GameScoreModel", back_populates="games")

class GameScoreModel(Base):
    "Game Score Model Class"
    __tablename__ = "game_scores"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    game_id = Column(Integer, ForeignKey('games.id'))
    score = Column(Integer)
    rank = Column(Integer)
    created_at = Column(DateTime, default=datetime.now)

    users = relationship("UserModel", back_populates="game_scores")
    games = relationship("GameModel", back_populates="game_scores")