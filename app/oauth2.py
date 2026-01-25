from fastapi import Depends, HTTPException,status
from jose import JWTError, jwt
from sqlmodel import Session
from .config import settings
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime,timedelta, timezone
from . import models,database

oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/login")

SECRET_KEY=settings.secret_key
ALGORITHM=settings.algorithm
EXPIRATION_TIME=settings.expiration_time

def get_token(data:dict):
    to_encode=data.copy()

    expire=datetime.now(timezone.utc) + timedelta(minutes=EXPIRATION_TIME)

    to_encode.update({"exp":expire})

    encoded_jwt =jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token:str, credentials_exception):
    try:
        data=jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])

        user_id: int = data.get("user_id")

        if not user_id:
            raise credentials_exception
        
        return user_id
        
    except JWTError:
        raise credentials_exception
    

def get_current_user(db:Session =Depends(database.get_session),token=Depends(oauth2_scheme)):
    credentials_exception= HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldnot validate credentials",headers={"WWW-Authenticate":"Bearer"})

    user_id=verify_token(token, credentials_exception)

    user=db.get(models.User, user_id)

    if not user:
        raise credentials_exception

    return user