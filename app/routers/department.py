# app/routers/department.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

# Importaciones necesarias
from app.database.database import get_db
from app.schemas import esquemas as schemas
# --- CAMBIO: Importamos el nuevo servicio ---
from app.services import department_service

# --- Router para Departamentos (sin cambios) ---
router = APIRouter(
   
    tags=["Departamentos"]
)

@router.get("/", response_model=List[schemas.Departamento])
def get_all_departments(db: Session = Depends(get_db)):
    """
    Obtiene una lista de todos los departamentos registrados en la base de datos.
    Esta ruta es la que consumirá el frontend para poblar el menú desplegable.
    """
    # --- CAMBIO: La lógica ahora se llama desde el servicio ---
    departments = department_service.get_all_departments(db=db)
    
    # La validación de si se encontraron o no, se queda en la ruta.
    if not departments:
        raise HTTPException(status_code=404, detail="No se encontraron departamentos")
    return departments

@router.post("/", response_model=schemas.Departamento, status_code=status.HTTP_201_CREATED)
def create_new_department(department: schemas.DepartamentoCreate, db: Session = Depends(get_db)):
    """
    Crea un nuevo departamento.
    """
    # --- CAMBIO: Llamamos al servicio para crear el departamento ---
    # El manejo de errores (como departamentos duplicados) ya está en el servicio.
    return department_service.create_department(db=db, department=department)

