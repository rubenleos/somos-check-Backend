# ===============================================================
# ARCHIVO: app/routers/asistencia.py
# PROPÓSITO: Contiene los endpoints para el registro de entradas y
#            salidas de los empleados (el checador).
# ===============================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime, timezone

# Importaciones de nuestro proyecto
from ..models import tablas as models
from ..schemas import esquemas as schemas
from ..database.database import get_db
from ..core.auth_utils import get_current_active_user

# Creamos un nuevo router para organizar estos endpoints
router = APIRouter(
    prefix="/asistencia",
    tags=["Asistencia (Checador)"]
)

@router.post("/check-in", response_model=schemas.RegistroAsistencia)
def registrar_check_in(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Registra la hora de entrada (check-in) para el usuario autenticado.
    Valida que no exista ya un registro abierto para el día de hoy.
    """
    hoy = datetime.now(timezone.utc).date()
    
    # 1. Verificar si ya hay un registro con check-in pero sin check-out para hoy
    registro_abierto = db.query(models.RegistroAsistencia).filter(
        models.RegistroAsistencia.id_usuario == current_user.id_usuario,
        models.RegistroAsistencia.fecha == hoy,
        models.RegistroAsistencia.hora_salida == None
    ).first()
    
    if registro_abierto:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya tienes un registro de entrada abierto para hoy. Debes hacer check-out primero."
        )

    # 2. Crear el nuevo registro de asistencia
    ahora_utc = datetime.now(timezone.utc)
    nuevo_registro = models.RegistroAsistencia(
        id_usuario=current_user.id_usuario,
        fecha=hoy,
        hora_entrada=ahora_utc
    )
    
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    
    return nuevo_registro

@router.put("/check-out", response_model=schemas.RegistroAsistencia)
def registrar_check_out(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Registra la hora de salida (check-out) para el usuario autenticado.
    Busca el registro de check-in abierto del día de hoy y le añade la hora de salida.
    """
    hoy = datetime.now(timezone.utc).date()
    
    # 1. Buscar el registro de check-in abierto para el día de hoy
    registro_a_cerrar = db.query(models.RegistroAsistencia).filter(
        models.RegistroAsistencia.id_usuario == current_user.id_usuario,
        models.RegistroAsistencia.fecha == hoy,
        models.RegistroAsistencia.hora_salida == None
    ).first()
    
    if not registro_a_cerrar:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró un registro de entrada abierto para hoy. Debes hacer check-in primero."
        )
        
    # 2. Actualizar la hora de salida
    ahora_utc = datetime.now(timezone.utc)
    
    # Validación simple: la hora de salida no puede ser anterior a la de entrada
    if ahora_utc < registro_a_cerrar.hora_entrada:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La hora de salida no puede ser anterior a la hora de entrada."
        )

    registro_a_cerrar.hora_salida = ahora_utc
    db.commit()
    db.refresh(registro_a_cerrar)
    
    return registro_a_cerrar

@router.get("/mis-registros", response_model=List[schemas.RegistroAsistencia])
def leer_mis_registros(
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Obtiene el historial de registros de asistencia para el usuario autenticado.
    Permite filtrar por un rango de fechas opcional.
    """
    query = db.query(models.RegistroAsistencia).filter(
        models.RegistroAsistencia.id_usuario == current_user.id_usuario
    )
    
    if fecha_inicio:
        query = query.filter(models.RegistroAsistencia.fecha >= fecha_inicio)
    if fecha_fin:
        query = query.filter(models.RegistroAsistencia.fecha <= fecha_fin)
        
    # Ordenar por fecha descendente para ver los más recientes primero
    registros = query.order_by(models.RegistroAsistencia.fecha.desc()).all()
    
    return registros

@router.get("/estado-hoy", response_model=schemas.RegistroAsistencia | None)
def obtener_estado_de_hoy(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Devuelve el registro de asistencia del día de hoy para el usuario autenticado.
    Útil para que el frontend sepa si el usuario ya hizo check-in, check-out o nada.
    Devuelve el registro o null si no hay actividad hoy.
    """
    hoy = datetime.now(timezone.utc).date()
    registro_hoy = db.query(models.RegistroAsistencia).filter(
        models.RegistroAsistencia.id_usuario == current_user.id_usuario,
        models.RegistroAsistencia.fecha == hoy
    ).first()
    
    return registro_hoy
