from fastapi import APIRouter, Depends,HTTPException, Response,status
from sqlmodel import select
from .. import models,schemas,database,rbac,oauth2
from typing import List

router=APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)

@router.post("/", response_model=models.Room)
def add_new_room(room_data:schemas.RoomCreate,db:database.SessionLocal,current_user:models.User=Depends(rbac.require_roles(["admin"]))):
    room=db.exec(select(models.Room).where(models.Room.room_number==room_data.room_number)).first()

    if room:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Room {room_data.room_number} already exists.")
    
    room=models.Room(**room_data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.get("/", response_model=List[models.Room])
def get_all_rooms(db:database.SessionLocal, current_user:models.User=Depends(oauth2.get_current_user)):
    rooms=db.exec(select(models.Room)).all()

    return rooms

@router.get("/{room_no}",response_model=models.Room)
def get_a_room(db:database.SessionLocal,room_no:int ,current_user:models.User=Depends(oauth2.get_current_user)):
    room=db.exec(select(models.Room).where(models.Room.room_number == room_no)).first()
    
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room {room_no} not found")

    return room

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
def delete_room(id:int, db:database.SessionLocal, current_user:models.User=Depends(rbac.require_roles(["admin"]))):
    room=db.exec(select(models.Room).where(models.Room.id == id)).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room {id} not found.")
    
    db.delete(room)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=models.Room)
def update_room(id:int, room_data: schemas.RoomCreate,db:database.SessionLocal, current_user:models.User=Depends(rbac.require_roles(["admin"]))):
    room=db.exec(select(models.Room).where(models.Room.id == id)).first()

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room {id} not found.")
    
    existing=db.exec(select(models.Room).where(models.Room.room_number == room_data.room_number, models.Room.id != id)).first()

    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Room with {room_data.room_number} already exists.")

    room_dict=room_data.model_dump()
    for key,value in room_dict.items():
        setattr(room,key,value)

    db.commit()
    db.refresh(room)

    return room


@router.patch("/{id}", response_model=models.Room)
def patch_post(id:int,db:database.SessionLocal, room_data:schemas.RoomPatch, current_user: models.User=Depends(rbac.require_roles(["admin"]))):
    room=db.get(models.Room,id)

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room {id} not found.")
    
    if room_data.room_number:
        existing=db.exec(select(models.Room).where(models.Room.room_number == room_data.room_number, models.Room.id != id)).first()

        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Room with {room_data.room_number} already exists.")

    
    room_dict=room_data.model_dump(exclude_unset=True)
    for key,value in room_dict.items():
        setattr(room,key,value)

    db.commit()
    db.refresh(room)

    return room
