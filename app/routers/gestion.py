# ===============================================================
# ARCHIVO: app/routers/gestion.py
# Propósito: Contiene los endpoints de la API para toda la lógica
#            de gestión administrativa: turnos, asignaciones,
#            solicitudes de eventos, etc.
# ===============================================================
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import date

# Importaciones de nuestro proyecto
from ..models import tablas as models
from ..schemas import esquemas as schemas
from ..database.database import get_db
# Asumimos que tienes un archivo con esta función para proteger rutas
from ..core.auth_utils import get_current_active_user

# Creamos un nuevo router para organizar estos endpoints
router = APIRouter(
    prefix="/gestion", # Todos los endpoints aquí empezarán con /gestion
    tags=["Gestión Administrativa"]
)

# --- CRUD para Tipos de Horario (Turnos) ---

@router.post("/turnos/", response_model=schemas.TipoHorario, status_code=status.HTTP_201_CREATED)
def crear_tipo_horario(
    turno: schemas.TipoHorarioCreate,
    db: Session = Depends(get_db),
    # Descomenta la siguiente línea si quieres que solo un admin pueda crear turnos
    # current_user: models.Usuario = Depends(get_admin_user)
):
    """
    Crea un nuevo tipo de horario o turno en el sistema.
    Idealmente, esta operación debería estar restringida a administradores.
    """
    db_turno = models.TipoHorario(**turno.model_dump())
    db.add(db_turno)
    db.commit()
    db.refresh(db_turno)
    return db_turno

@router.get("/turnos/", response_model=List[schemas.TipoHorario])
def leer_tipos_horario(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Obtiene una lista de todos los tipos de horario disponibles.
    """
    turnos = db.query(models.TipoHorario).offset(skip).limit(limit).all()
    return turnos

# --- CRUD para Asignación de Horarios ---

@router.post("/asignaciones/", response_model=schemas.AsignacionHorario, status_code=status.HTTP_201_CREATED)
def crear_asignacion_horario(
    asignacion: schemas.AsignacionHorarioCreate,
    db: Session = Depends(get_db)
):
    """
    Asigna un turno específico a un usuario en una fecha determinada.
    """
    # La restricción UNIQUE en el modelo previene duplicados (mismo usuario, misma fecha)
    db_asignacion = models.AsignacionHorario(**asignacion.model_dump())
    try:
        db.add(db_asignacion)
        db.commit()
        db.refresh(db_asignacion)
        return db_asignacion
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El usuario ya tiene un turno asignado para esta fecha."
        )

@router.get("/asignaciones/usuario/{usuario_id}", response_model=List[schemas.AsignacionHorario])
def leer_asignaciones_por_usuario(
    usuario_id: int,
    fecha_inicio: date,
    fecha_fin: date,
    db: Session = Depends(get_db)
):
    """
    Obtiene todas las asignaciones de horario para un usuario específico
    dentro de un rango de fechas.
    """
    asignaciones = db.query(models.AsignacionHorario).filter(
        models.AsignacionHorario.id_usuario == usuario_id,
        models.AsignacionHorario.fecha >= fecha_inicio,
        models.AsignacionHorario.fecha <= fecha_fin
    ).all()
    
    if not asignaciones:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron asignaciones para el usuario en el rango de fechas especificado."
        )
    return asignaciones

# --- CRUD para Eventos Adicionales (Vacaciones, Permisos, etc.) ---

@router.post("/eventos/", response_model=schemas.EventoAdicional, status_code=status.HTTP_201_CREATED)
def solicitar_evento(
    evento: schemas.EventoAdicionalCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Permite a un usuario autenticado crear una solicitud de evento 
    (ej. vacaciones, permiso). El estado inicial será 'PENDIENTE'.
    """
    # Aseguramos que el usuario solo pueda crear eventos para sí mismo.
    if evento.id_usuario != current_user.id_usuario:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No puedes crear eventos para otro usuario.")

    db_evento = models.EventoAdicional(**evento.model_dump())
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    return db_evento

@router.get("/eventos/mis-solicitudes", response_model=List[schemas.EventoAdicional])
def leer_mis_solicitudes_de_evento(
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(get_current_active_user)
):
    """
    Devuelve una lista de todas las solicitudes de eventos hechas por el 
    usuario actualmente autenticado.
    """
    eventos = db.query(models.EventoAdicional).filter(models.EventoAdicional.id_usuario == current_user.id_usuario).all()
    return eventos

@router.put("/eventos/{evento_id}/estado", response_model=schemas.EventoAdicional)
def actualizar_estado_evento(
    evento_id: int,
    actualizacion: schemas.EventoAdicionalUpdate,
    db: Session = Depends(get_db)
    # Aquí es MUY recomendable tener una dependencia que verifique si el usuario es admin
    # current_user: models.Usuario = Depends(get_admin_user)
):
    """
    Permite a un administrador aprobar o rechazar una solicitud de evento.
    """
    db_evento = db.query(models.EventoAdicional).filter(models.EventoAdicional.id_evento == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Evento no encontrado.")

    # Validar que el estado sea uno de los permitidos
    estados_validos = ['APROBADO', 'RECHAZADO', 'PENDIENTE']
    if actualizacion.estado.upper() not in estados_validos:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Estado no válido. Use uno de: {estados_validos}")

    db_evento.estado = actualizacion.estado.upper()
    db.commit()
    db.refresh(db_evento)
    return db_evento

@router.get("/eventos/", response_model=List[schemas.EventoAdicional])
def leer_todos_los_eventos(
    db: Session = Depends(get_db),
    estado: str | None = None # Permite filtrar por ej: /eventos/?estado=PENDIENTE
    # current_user: models.Usuario = Depends(get_admin_user)
):
    """
    Obtiene una lista de todos los eventos del sistema.
    Opcionalmente puede filtrarse por estado. (Ideal para admins)
    """
    query = db.query(models.EventoAdicional)
    if estado:
        query = query.filter(models.EventoAdicional.estado.ilike(f"%{estado}%"))
    
    eventos = query.all()
    return eventos
