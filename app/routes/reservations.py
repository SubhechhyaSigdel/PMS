from fastapi import APIRouter
from .. import models,database

router=APIRouter(
    prefix="/reservations",
    tags=['Reservations']
)

@router.post("/", response_model=models.Reservation)
def create_reservation(db:database.SessionLocal,reservation_data):
    pass