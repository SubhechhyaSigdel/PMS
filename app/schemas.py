from datetime import date, datetime
from decimal import Decimal
from pydantic import EmailStr
from sqlmodel import SQLModel
from . import models
from typing import List, Optional

# Base Room Schema

class RoomBase(SQLModel):
    room_number: int
    room_type: models.RoomType
    capacity: int
    price: Decimal
    status: models.RoomStatus
    is_active: Optional[bool]=True

class RoomCreate(RoomBase):
    pass

class RoomUpdate(RoomBase):
    pass

class RoomStatusUpdate(SQLModel):
    status:models.RoomStatus

class RoomResponse(RoomBase):
    id:int 
    is_active:bool

    class Config:
        from_attributes=True
        
#Token

class TokenResponse(SQLModel):
    access_token:str
    token_type:str = "bearer"

class TokenData(SQLModel):
    id:Optional[int] = None

#User schema

class UserBase(SQLModel):
    username: str

class UserCreate(UserBase):
    password: str
    roles: models.Roles

class UserResponse(UserBase):
    id:int
    roles:List[str]

    class Config:
        from_attributes=True

#Guest schema

class GuestBase(SQLModel):
    name:str
    phone:str
    email:EmailStr

class GuestCreate(GuestBase):
    pass

class GuestResponse(GuestBase):
    id:int

    class Config:
        from_attributes=True

#Reservation schemes
class ReservationBase(SQLModel):
    guest_id: Optional[int]
    room_id:int
    check_in:date
    check_out:date
    no_of_guests: int
    per_night_rate: Decimal

class ReservationCreate(ReservationBase):
    pass

class ReservationUpdate(ReservationBase):
    check_in: Optional[date]=None
    check_out:Optional[date]=None
    no_of_guests:Optional[int]=None
    status: Optional[models.ReservationStatus] = None

class ReservationResponse(ReservationBase):
    id: int
    created_at: datetime
    status: models.ReservationStatus

    class Config:
        from_attributes=True

#Bill schemes

class BillBase(SQLModel):
    total_amount: Decimal

class BillCreate(BillBase):
    reservation_id : int

class BillResponse(BillBase):
    id: int
    reservation_id : int
    paid: bool
    created_at: datetime

    class Config:
        from_attributes=True