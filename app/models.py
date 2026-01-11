from datetime import date, datetime
from pydantic import EmailStr
from sqlmodel import Column, Field, ForeignKey, Integer, SQLModel
from enum import StrEnum
from sqlalchemy import CheckConstraint

class Roles(StrEnum):
    ADMIN = "admin"
    STAFF = "staff"

class RoomStatus(StrEnum):
    AVAILABLE="available"
    OCCUPIED="occupied"
    MAINTENANCE="maintenance"

class ReservationStatus(StrEnum):
    RESERVED="reserved"
    CHECKED_IN="checked_in"
    CHECKED_OUT="checked_out"
    CANCELLED="cancelled"

class RoomType(StrEnum):
    SINGLE="single"
    DOUBLE="double"

class Room(SQLModel, table=True):
    __tablename__= "rooms"
    id: int | None = Field(default=None, primary_key=True)
    room_number: int = Field(unique=True)
    room_type:RoomType
    capacity:int
    price: float
    status: RoomStatus

class Guests(SQLModel, table=True):
    __tablename__="guests"
    id: int | None=Field(default=None, primary_key=True)
    name: str
    phone: str
    email: EmailStr = Field(unique=True)

class Reservation(SQLModel, table=True):
    __tablename__="reservations"
    id:int | None=Field(default=None,primary_key=True)
    guest_id : int=Field(sa_column=Column(Integer,ForeignKey("guests.id", ondelete="CASCADE")))
    room_id : int=Field(sa_column=Column(Integer,ForeignKey("rooms.id", ondelete="CASCADE")))
    check_in: date
    check_out: date
    per_night_rate: float
    created_at: datetime | None = Field(default_factory=datetime.utcnow)
    status: ReservationStatus
    __tableargs__= CheckConstraint("check_in < check_out", name="check_check_in_before_check_out")

class Bill(SQLModel, table=True):
    __tablename__="bills"
    id: int | None=Field(default=None, primary_key=True)
    reservation_id: int = Field(sa_column=Column(Integer, ForeignKey("reservations.id", ondelete="CASCADE")))
    total_amount:float
    paid : bool | None= Field(default=False)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)

    
class User(SQLModel, table=True):
    __tablename__="users"
    id: int | None=Field(default=None, primary_key=True)
    username: str = Field(default=None, unique=True)
    hashed_password:str
    role: Roles


