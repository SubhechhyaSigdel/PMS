from . import models
from .oauth2 import get_current_user
from fastapi import Depends, HTTPException, status

def require_roles(allowed_roles: list[str]):
    def role_checker(user: models.User = Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access Denied")
        return user
    return role_checker