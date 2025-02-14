"""Schema Module For Database Models"""

from pydantic import BaseModel
from typing import Optional
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


class GameSessionCreate(GameSessionBase):
    pass

class GameSessionResponse(GameSessionCreate):
    id: int
    game_status: str
    start_time: datetime
    end_time: Optional[datetime] = None

class GameStatusBase(BaseModel):
    game_id: int

class GameStatusResponse(GameStatusBase):
    id: int
    started_at: datetime
    ended_at: Optional[datetime] = None
    number_of_users_joined: int
    status: str

class LeaderboardResponse(BaseModel):
    user_id: int
    score: int