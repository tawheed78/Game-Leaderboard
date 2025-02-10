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
    upvotes: int

class GameSessionBase(BaseModel):
    user_id: int
    game_id: int
    score: int
    start_time: datetime


class GameSessionCreate(GameSessionBase):
    pass

class GameSessionResponse(GameSessionCreate):
    id: int
    game_status: str
    end_time: Optional[datetime] = None

class LeaderboardResponse(BaseModel):
    user_id: int
    score: int