# ===============================================================
# ARCHIVO: app/services/department_service.py
# PROPÓSITO: Contiene la lógica de negocio para gestionar los
#            departamentos (crear, obtener, etc.).
# ===============================================================
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from typing import List

# Usamos la ruta de importación correcta basada en tu proyecto
from app.models import tablas as models
from app.schemas import esquemas as schemas

def get_all_departments(db: Session) -> List[models.Departamento]:
    """
    Obtiene una lista de todos los departamentos de la base de datos,
    ordenados por nombre.
    """
    print("\n--- [SERVICIO] Intentando obtener todos los departamentos... ---")
    
    # Esta es la consulta que se va a ejecutar
    query = db.query(models.Departamento).order_by(models.Departamento.nombre_depto)
    
    # Ejecutamos la consulta
    all_departments = query.all()
    
    # --- AÑADIDO PARA DEPURAR ---
    # Imprimimos la cantidad de resultados encontrados antes de devolverlos.
    print(f"--- [SERVICIO] Consulta ejecutada. Se encontraron: {len(all_departments)} departamentos. ---")
    
    return all_departments

def create_department(db: Session, department: schemas.DepartamentoCreate) -> models.Departamento:
    """
    Crea un nuevo departamento en la base de datos.
    """
    print(f"--- Intentando crear el departamento: {department.nombre_depto} ---")
    
    # Creamos la nueva instancia del modelo de SQLAlchemy
    new_department = models.Departamento(**department.dict())
    
    try:
        db.add(new_department)
        db.commit()
        db.refresh(new_department)
        print(f"--- Departamento '{new_department.nombre_depto}' creado exitosamente. ---")
        return new_department
    except IntegrityError:
        # Este error ocurre si el nombre del departamento ya existe (debido al 'unique=True' en el modelo)
        db.rollback()
        print(f"--- ERROR: El departamento '{department.nombre_depto}' ya existe. ---")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El departamento con el nombre '{department.nombre_depto}' ya existe."
        )

