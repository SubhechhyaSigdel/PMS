from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response,status
from sqlmodel import Session, select
from .. import models,schemas,rbac,database,utils,oauth2

router=APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/",response_model=schemas.UserResponse)
def create_user(
    user_data:schemas.UserCreate,
    db=Depends(database.get_session)): #current_user:models.User=Depends(rbac.require_roles(["admin"]))):

    existing_user=db.exec(select(models.User).where(models.User.username == user_data.username)).first()

    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User with username '{user_data.username}' already exists.")
    
    hashed_password=utils.hash(user_data.password)

    user=models.User(username=user_data.username, hashed_password=hashed_password, role=user_data.role)

    db.add(user)
    db.commit()
    db.refresh(user)

    return user

@router.get("/", response_model=List[schemas.UserResponse])
def get_users(
    db:database.SessionLocal,user:models.User=Depends(rbac.require_roles(["admin"]))):
    users = db.exec(select(models.User)).all()

    return users

@router.get("/me", response_model=schemas.UserResponse)
def get_current_user(current_user:models.User=Depends(oauth2.get_current_user)):
    return current_user

@router.get("/{id}", response_model=schemas.UserResponse)
def get_a_user(id:int, 
    db:database.SessionLocal,current_user:models.User=Depends(rbac.require_roles(["admin"]))):

    user=db.get(models.User,id)
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"User with id: {id} not found.")
    
    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id:int,
    db:database.SessionLocal, 
    current_user:models.User=Depends(rbac.require_roles(["admin"]))):
    
    user=db.get(models.User, id)

    if not user:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with id: {id} not found.")

    db.delete(user)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
