from passlib.context import CryptContext
from . import models

pwd_context=CryptContext(schemes=["bcrypt"], deprecated=["auto"])

def hash(password):
    return pwd_context.hash(password)

def verify(plain_password,hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def calculate_bill_total(reservation:models.reservation):
    total=(reservation.check_out - reservation.check_in).days * reservation.per_night_rate
