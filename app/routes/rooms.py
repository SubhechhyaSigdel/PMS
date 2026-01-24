from fastapi import APIRouter, Depends,HTTPException, status
from sqlmodel import Session, select, asc
from .. import models,schemas,database,rbac,oauth2
from typing import List, Optional

router=APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)

@router.post("/", response_model=models.Room)
def add_new_room(room_data:schemas.RoomCreate,db:database.SessionLocal,current_user:models.User=Depends(rbac.require_roles(["admin"]))):

    existing_room=db.exec(select(models.Room).where(models.Room.room_number==room_data.room_number)).first()

    if existing_room:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Room {room_data.room_number} already exists.")
    
    room = models.Room(**room_data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)

    return room

@router.get("/", response_model=List[models.Room])
def get_all_rooms(
    db:database.SessionLocal,
    current_user:models.User=Depends(oauth2.get_current_user),
    query_status: Optional[models.RoomStatus]=None, 
    include_inactive: Optional[bool]=False):
    
    query=select(models.Room).order_by(asc(models.Room.room_number))

    if include_inactive and current_user.role != ["admin"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view inactive rooms.")
    
    if not include_inactive:
        query=query.where(models.Room.is_active == True)

    if query_status:
        query=query.where(models.Room.status == query_status)

    rooms=db.exec(query).all()

    return rooms

@router.get("/{room_id}",response_model=models.Room)
def get_a_room(
    room_id:int,
    db:database.SessionLocal,
    current_user:models.User=Depends(oauth2.get_current_user)):

    room=db.get(models.Room, room_id)
    
    if not room or (not room.is_active and current_user.role != "admin"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Room with id:{room_id} not found")

    return room


# @router.delete("/{room_id}",status_code=status.HTTP_204_NO_CONTENT)
# def delete_room(id:int, db:database.SessionLocal, current_user:models.User=Depends(rbac.require_roles(["admin"]))):
#     room=db.get(models.Room, room_id)

#     if not room:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room with id: {room_id} not found.")
    
#     db.delete(room)
#     db.commit()

#     return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{room_id}/soft", response_model=models.Room)
def soft_delete_room(
    room_id:int, 
    db:database.SessionLocal,
    current_user:models.User=Depends(rbac.require_roles(["admin"]))):

    #  Soft delete a room by marking it inactive.

    room=db.get(models.Room, room_id)

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room with id: {room_id} not found.")
    
    room.is_active=False
    room.status=models.RoomStatus.INACTIVE

    db.commit()
    db.refresh(room)
    return room


#Restore soft deleted room

@router.patch("/{room_id}/restore", response_model=models.Room)
def restore_room(
    room_id:int, 
    db:database.SessionLocal,
    current_user:models.User=Depends(rbac.require_roles(["admin"]))):

#Restore a soft-deleted room to active status
    room=db.get(models.Room, room_id)

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room with id: {room_id} not found.")
    
    room.is_active=True
    room.status=models.RoomStatus.AVAILABLE
    db.commit()
    db.refresh(room)

    return room

#Update room information

@router.patch("/{room_id}", response_model=models.Room)
def update_room_info(
    room_id : int,
    updated_room:schemas.RoomUpdate, db:database.SessionLocal,
    current_user: models.User=Depends(rbac.require_roles(["admin"]))):

    room=db.get(models.Room, room_id)

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room with id: {room_id} not found.")
    
    if updated_room.room_number:

        existing=db.exec(select(models.Room).where(models.Room.room_number == updated_room.room_number, models.Room.id != room_id)).first()

        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
            detail=f"Room {updated_room.room_number} already exists.")
        
    if not room.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,detail="Restore room before updating.")
    
    room_data=updated_room.model_dump(exclude_unset=True)
    for key,value in room_data.items():
        setattr(room,key,value)

    db.commit()
    db.refresh(room)

    return room


#update room status only

@router.patch("/{room_id}/status", response_model=models.Room)
def update_room_status(
    room_id:int, 
    new_status: schemas.RoomStatusUpdate, 
    db: Session = Depends(database.get_session), 
    current_user:models.User=Depends(oauth2.get_current_user)):

    room=db.get(models.Room, room_id)

    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Room with id: {room_id} not found.")
    
    if not room.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot update status for inactive rooms.")
    
    room.status=new_status.status

    db.commit()
    db.refresh(room)

    return room