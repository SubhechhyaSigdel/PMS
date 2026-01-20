from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List, Optional
from pydantic import EmailStr
from sqlmodel import Column, Field, ForeignKey, Integer, Relationship, SQLModel,Numeric
from enum import StrEnum
from sqlalchemy import CheckConstraint, Enum as SAEnum

class Roles(StrEnum):
    ADMIN = "admin"
    STAFF = "staff"

class RoomStatus(StrEnum):
    AVAILABLE="available"
    OCCUPIED="occupied"
    MAINTENANCE="maintenance"
    INACTIVE="inactive"

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
    room_type:RoomType = Field(sa_column=Column(SAEnum(RoomType,name="room_type")))
    capacity:int
    price: Decimal=Field(sa_column=Column(Numeric(10,2)))
    status: RoomStatus = Field(sa_column=Column(SAEnum(RoomStatus, name="room_status")))
    is_active: bool | None = Field(default=True)
    reservations: List["Reservation"] = Relationship(back_populates="room")
    __table_args__=(CheckConstraint("capacity > 0", name="check_capacity_more_than_zero"),
                    CheckConstraint("price > 0", name="check_price_more_than_zero")
    )

class Guest(SQLModel, table=True):
    __tablename__="guests"
    id: int | None=Field(default=None, primary_key=True)
    name: str
    phone: str
    email: EmailStr = Field(unique=True)
    reservations: List["Reservation"] = Relationship(
        back_populates="guest",
        sa_relationship_kwargs={"passive_deletes":True}
    )

class Reservation(SQLModel, table=True):
    __tablename__="reservation"
    id:int | None=Field(default=None,primary_key=True)
    guest_id : Optional[int]=Field(sa_column=Column(Integer,ForeignKey("guests.id", ondelete="CASCADE"), nullable=True))
    room_id : int=Field(sa_column=Column(Integer,ForeignKey("rooms.id", ondelete="CASCADE")))
    check_in: date
    check_out: date
    no_of_guests:int
    per_night_rate: Decimal=Field(sa_column=Column(Numeric(10,2)))
    created_at: datetime | None = Field(default_factory=lambda:datetime.now(timezone.utc))
    status: ReservationStatus = Field(sa_column=Column(SAEnum(ReservationStatus, name="reservation_status")))
    guest: Optional["Guest"] = Relationship(back_populates="reservations")
    room: "Room" = Relationship(back_populates="reservations")
    bill: Optional["Bill"] = Relationship(
        back_populates="reservation",
        sa_relationship_kwargs={"passive_deletes":True, "uselist":False}
    )
    __table_args__= (CheckConstraint("check_in < check_out", name="check_check_in_before_check_out"),
                    CheckConstraint("per_night_rate > 0",name="check_per_night_rate_is_not_zero"),
                    CheckConstraint("no_of_guests > 0", name="check_no_of_guest_not_zero")
                                   )

class Bill(SQLModel, table=True):
    __tablename__ ="bills"
    id: int | None=Field(default=None, primary_key=True)
    reservation_id: int = Field(sa_column=Column(Integer, ForeignKey("reservation.id", ondelete="CASCADE")))
    total_amount:Decimal=Field(sa_column=Column(Numeric(10,2)))
    paid : bool | None= Field(default=False)
    created_at: datetime | None = Field(default_factory=lambda:datetime.now(timezone.utc))
    reservation: "Reservation" = Relationship(back_populates="bill",
                                            sa_relationship_kwargs={"passive_deletes":True})


class User(SQLModel, table=True):
    __tablename__: str = "users"
    id: int | None=Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    hashed_password:str
    role: Roles = Field(sa_column=Column(SAEnum(Roles, name="roles")))
