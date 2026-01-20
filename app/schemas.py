from sqlmodel import SQLModel
from . import models
from typing import Optional

class UserResponse(SQLModel):
    id: int
    username: str
    role: str

class UserCreate(SQLModel):
    username:str
    password:str
    role: models.Roles

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

class RoomUpdate(SQLModel):
    room_number: int | None
    room_type: models.RoomType |  None
    capacity:int |  None
    price: float |  None
    status: models.RoomStatus | None