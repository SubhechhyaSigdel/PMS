from typing import List
from fastapi import APIRouter, Depends,HTTPException, status
from sqlalchemy import select
from sqlmodel import Session
from .. import models,schemas, database,rbac,oauth2

router=APIRouter(
    prefix="/guests",
    tags=["Guests"]
)

#Create guest
@router.post("/", response_model=schemas.GuestResponse)
def create_guest(guest_data: schemas.GuestCreate, db: Session=Depends(database.get_session),
    current_user:models.User=Depends(rbac.require_roles(["admin","staff"]))):

    existing_guest= db.exec(select(models.Guest).where(models.Guest.email == guest_data.email)).first()

    if existing_guest:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Guest with email {guest_data.email} already exists.")
    
    guest= models.Guest(**guest_data.model_dump())

    db.add(guest)
    db.commit()
    db.refresh(guest)

    return guest

#get all guests
@router.get("/", response_model=List[schemas.GuestResponse])
def get_all_guests(db: Session = Depends(database.get_session),current_user: models.User=Depends(oauth2.get_current_user)):
    
    guests=db.exec(select(models.Guest)).all()
    return guests

#get guest by id
@router.get("/{guest_id}", response_model=schemas.GuestResponse)
def get_guest_by_id(guest_id: int, db: Session=Depends(database.get_session),
                    current_user:models.User=Depends(oauth2.get_current_user)):
    
    guest= db.get(models.Guest, guest_id)

    if not guest:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Guest with id {guest_id} not found.")
    return guest