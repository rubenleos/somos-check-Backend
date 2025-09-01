from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database.database import get_db
from app.models import tablas as models
from app.schemas.user import UserOut, UserWithDeptOut   # <— importa clases reales

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=List[UserOut])  # <— sin comillas
def get_users_by_department(
    id_departamento: int = Query(...),
    q: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(models.Usuario).filter(models.Usuario.id_departamento == id_departamento)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(models.Usuario.numero_empleado.ilike(like),
                                 models.Usuario.nombre_completo.ilike(like)))
    # devolvemos modelos; Pydantic v2 los mapea gracias a from_attributes=True
    return query.order_by(models.Usuario.id_usuario.desc()).offset(offset).limit(limit).all()


@router.get("/with-dept", response_model=List[UserWithDeptOut])
def get_users_by_department_with_name(
    id_departamento: int = Query(...),
    q: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(
        models.Usuario.id_usuario,
        models.Usuario.numero_empleado,
        models.Usuario.nombre_completo,
        models.Usuario.email,
        models.Usuario.id_departamento,
        models.Departamento.nombre_depto,
    ).join(
        models.Departamento,
        models.Departamento.id_departamento == models.Usuario.id_departamento
    ).filter(
        models.Usuario.id_departamento == id_departamento
    )

    if q:
        like = f"%{q}%"
        query = query.filter(or_(models.Usuario.numero_empleado.ilike(like),
                                 models.Usuario.nombre_completo.ilike(like)))

    rows = query.order_by(models.Usuario.id_usuario.desc()).offset(offset).limit(limit).all()

    # mapeamos explícito a schema (porque estamos retornando columnas, no modelos)
    return [
        UserWithDeptOut(
            id_usuario=r.id_usuario,
            numero_empleado=r.numero_empleado,
            nombre_completo=r.nombre_completo,
            email=r.email,
            id_departamento=r.id_departamento,
            nombre_depto=r.nombre_depto,
        )
        for r in rows
    ]
