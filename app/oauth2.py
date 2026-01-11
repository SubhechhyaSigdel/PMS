from fastapi import Depends, HTTPException,status
from jose import JWTError, jwt
from .config import settings
from fastapi.security.oauth2 import OAuth2PasswordBearer
from datetime import datetime,timedelta
from .database import SessionLocal
from . import models


oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")

SECRET_KEY=settings.secret_key
ALGORITHM=settings.algorithm
EXPIRATION_TIME=settings.expiration_time

def get_token(data:dict):
    expire=datetime.utcnow() + timedelta(minutes=EXPIRATION_TIME)
    data.update({"exp":expire})
    token=jwt.encode(data,SECRET_KEY,algorithm=ALGORITHM)
    return token

def verify_token(token:str, credentials_exception):
    try:
        data=jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])

        id=data["user_id"]

        if not id:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    return id

def get_current_user(db:SessionLocal, token=Depends(oauth2_scheme)):
    credentials_exception= HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldnot validate credentials",headers={"WWW-Authenticate":"Bearer"})

    id=verify_token(token, credentials_exception)

    user=db.get(models.User, id)

    return user

