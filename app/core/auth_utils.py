# app/core/auth_utils.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .security import SECRET_KEY, ALGORITHM, TokenData
from ..models import tablas as models
from ..schemas import esquemas as schemas
from ..database.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token") # La URL no se usará directamente, pero es necesaria

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.Usuario).filter(models.Usuario.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: models.Usuario = Depends(get_current_user)):
    # Aquí podrías añadir lógica para ver si el usuario está activo, etc.
    return current_user

