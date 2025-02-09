from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str
    password: str

class UserCreate(UserBase):
    created_at: datetime
    updated_at: datetime

class UserUpdate(UserBase):
    updated_at: datetime

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class config:
        from_attributes = True


class GameBase(BaseModel):
    title: str
    description: str
    created_at: datetime

class GameCreate(GameBase):
    pass

class GameResponse(GameBase):
    id: int


class GameScoreBase(BaseModel):
    user_id: int
    game_id: int
    score: int
    created_at: datetime

class GameScoreCreate(GameScoreBase):
    pass

class GameScoreResponse(GameScoreBase):
    id: int

class LeaderboardResponse(BaseModel):
    user_id: int
    score: int