from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from .. import models,database,schemas,rbac,oauth2
from sqlmodel import Session, select

router=APIRouter(
    prefix="/reservations",
    tags=['Reservations']
)

#create reservation

@router.post("/", response_model=models.Reservation)
def create_reservation(
    reservation_data: models.Reservation, 
    db: Session = Depends(database.get_session), current_user: models.User= Depends(rbac.require_roles(["admin", "staff"]))):

    room = db.get(models.Room, reservation_data.room_id)

    if not room or not room.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room with id {reservation_data.room_id} not found or inactive.")
    
    if room.status != models.RoomStatus.AVAILABLE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Room {room.room_number} is not available for reservation.")
    

    #validate dates
    if reservation_data.check_out >= reservation_data.check_in:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Check-out date must be after check-in date.")
    
    #validate guest exists
    guest= db.get(models.Guest, reservation_data.guest_id)

    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Guest with id {reservation_data.guest_id} not found.")
    
    per_night_rate = room.price

    reservation= models.Reservation(
        guest_id=guest.id,
        room_id=room.id,
        check_in=reservation_data.check_in,
        check_out=reservation_data.check_out,
        no_of_guests=reservation_data.no_of_guests,
        per_night_rate=per_night_rate,
        status=models.ReservationStatus.RESERVED
    )

    db.add(reservation)
    db.commit()
    db.refresh(reservation)

    #update room status to occupied if check-in date is today
    if reservation.check_in == date.today():
        room.status = models.RoomStatus.OCCUPIED
        db.commit()
        db.refresh(room)

        return reservation
    
#Get all reservations

@router.get("/", response_model=List[models.Reservation])
def get_all_reservations(
    db: Session = Depends(database.get_session),
    current_user: models.User = Depends(oauth2.get_current_user)):

#admin can see all reservations, staff sees only future reservations.
    query= select(models.Reservation)
    if current_user.role== "staff":
        query= query.where(models.Reservation.check_out >= date.today())

    reservations = db.exec(query).all()

    return reservations

#get reservation by id 
@router.get("/{reservation_id}", response_model=models.Reservation)
def get_reservation_by_id(
    reservation_id:int,
    db: Session = Depends(database.get_session),
    current_user: models.User = Depends(oauth2.get_current_user)):

    reservation= db.get(models.Reservation, reservation_id)

    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Reservation with id {reservation_id} not found.")
    
    return reservation

#Update reservation status
@router.patch("/{reservation_id}/status", response_model=models.Reservation)
def update_reservation_status(
    reservation_id : int,
    new_status: models.ReservationStatus,
    db: Session = Depends(database.get_session),
    current_user: models.User = Depends(rbac.require_roles(["admin", "staff"]))):

    reservation= db.get(models.Reservation, reservation_id)

    if not reservation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Reservation with id {reservation_id} not found.")
    
    reservation.status = new_status
    db.commit()
    db.refresh(reservation)

    #update room status based on reservation

    room= db.get(models.Room, reservation.room_id)
    if new_status == models.ReservationStatus.CHECKED_IN:
        room_status = models.RoomStatus.OCCUPIED

    elif new_status in [models.ReservationStatus.CHECKED_OUT, models.ReservationStatus.CANCELLED]:
        room_status= models.RoomStatus.AVAILABLE

    db.commit()
    db.refresh(room)

    return reservation