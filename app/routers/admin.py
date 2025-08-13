# app/routers/admin.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..models import tablas as models
from ..schemas import esquemas as schemas
from ..database.database import get_db

router = APIRouter()

# --- CRUD para Roles ---
@router.post("/roles/", response_model=schemas.Rol, status_code=status.HTTP_201_CREATED)
def crear_rol(rol: schemas.RolCreate, db: Session = Depends(get_db)):
    db_rol = models.Rol(nombre_rol=rol.nombre_rol)
    db.add(db_rol)
    db.commit()
    db.refresh(db_rol)
    return db_rol

@router.get("/roles/", response_model=List[schemas.Rol])
def leer_roles(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    roles = db.query(models.Rol).offset(skip).limit(limit).all()
    return roles

# TU TAREA: Crea los endpoints para Departamentos aquí, siguiendo el mismo patrón de Roles.

# --- CRUD para Usuarios ---
@router.post("/usuarios/", response_model=schemas.Usuario, status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    # Lógica para verificar si el email o numero_empleado ya existe...
    db_usuario = models.Usuario(**usuario.model_dump())
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.get("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def leer_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == usuario_id).first()
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario