from sqlmodel import SQLModel
from .models import Roles
from . import models
from typing import Optional

class UserResponse(SQLModel):
    id: int
    username: str
    role: Roles

class UserCreate(SQLModel):
    username:str
    password:str
    role: Roles

class TokenResponse(SQLModel):
    access_token:str
    token_type:str


class RoomCreate(SQLModel):
    room_number: int
    room_type: models.RoomType
    capacity: int
    price: float
    status: models.RoomStatus

class RoomStatusUpdate(SQLModel):
    status: models.RoomStatus 

class RoomPatch(SQLModel):
    room_number: Optional[int] = None
    room_type: Optional[models.RoomType] = None
    capacity: Optional[int] = None
    price: Optional[float] = None
    status: Optional[models.RoomStatus] = None