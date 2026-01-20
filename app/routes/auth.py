from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlmodel import select
from .. import schemas, models, oauth2,database,utils

router=APIRouter(
    prefix="/login",
    tags=["Authentication"]
)

@router.post("/", response_model=schemas.TokenResponse)
def login(db:database.SessionLocal, user_credentials:OAuth2PasswordRequestForm=Depends()):
    user=db.exec(select(models.User).where(models.User.username==user_credentials.username)).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials.")
    
    if not utils.verify(user_credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials.")
    
    token= oauth2.get_token({"user_id":user.id})

    return {
       "access_token":token,
       "token_type":"bearer"
    }