from fastapi import Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException
from typing import Optional
from datetime import timedelta, datetime, timezone
from jose import jwt
from sqlalchemy.orm import Session

from app.api.dependencies.database import get_db
from app.config import Config
from app.services.user_service import UserService

oauth2_scheme =  OAuth2PasswordBearer(tokenUrl = Config.URL_PREFIX+"auth/token")

def create_access_token(data : dict, expire_delta : Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expire_delta if expire_delta else timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp" : expire})
    return jwt.encode(to_encode, key=Config.SECRET_KEY, algorithm=Config.TOKEN_ALGORITHM)

def get_current_user(token : str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",  
        headers={"WWW-Authenticate": "Bearer"}, 
    )
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.TOKEN_ALGORITHM])
        user_name = payload.get("sub")
        if user_name is None:
            raise credentials_exception
    except jwt.JWTError:
        raise credentials_exception
    user = UserService.get_user_by_username(db=db, username=user_name)
    if not user or user is None:
        raise credentials_exception
    return user
