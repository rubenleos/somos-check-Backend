# ===============================================================
# ARCHIVO: app/services/attendance_service.py (Corregido)
# PROPÓSITO: Contiene la lógica de negocio para registrar la
#            asistencia usando la fecha y hora local del servidor.
# ===============================================================
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime # No se necesita timezone aquí

from app.models import tablas as models
from app.schemas import esquemas as schemas

def register_attendance(db: Session, usuario: models.Usuario):
    """
    Registra la asistencia para un usuario usando la fecha y hora local.
    - Si no hay un check-in abierto hoy, crea uno nuevo.
    - Si ya hay un check-in abierto, lo cierra (check-out).
    """
    user_id = usuario.id_usuario
    ahora = datetime.now()
    hoy = ahora.date()

    # 1. Buscar si hay un registro de check-in abierto para el día de hoy
    registro_abierto = db.query(models.RegistroAsistencia).filter(
        models.RegistroAsistencia.id_usuario == user_id,
        models.RegistroAsistencia.fecha == hoy,
        models.RegistroAsistencia.hora_salida == None
    ).first()

    if registro_abierto:
        # --- Lógica de Check-out ---
        print(f"Cerrando registro de asistencia para el usuario ID: {user_id}")
        registro_abierto.hora_salida = ahora
        db.commit()
        db.refresh(registro_abierto)
        
        return {
            "mensaje": "Salida (Check-out) registrada correctamente.",
            "data": schemas.RegistroAsistencia.model_validate(registro_abierto)
        }
    else:
        # --- Lógica de Check-in ---
        print(f"Creando nuevo registro de asistencia para el usuario ID: {user_id}")
        
        # --- INICIO DE LA CORRECCIÓN ---
        # Se añade el 'numero_empleado' al crear el nuevo registro.
        nuevo_registro = models.RegistroAsistencia(
            id_usuario=user_id,
            numero_empleado=usuario.numero_empleado, # <-- LÍNEA AÑADIDA
            fecha=hoy,
            hora_entrada=ahora
        )
        # --- FIN DE LA CORRECCIÓN ---
        
        db.add(nuevo_registro)
        db.commit()
        db.refresh(nuevo_registro)
        
        return {
            "mensaje": "Entrada (Check-in) registrada correctamente.",
            "data": schemas.RegistroAsistencia.model_validate(nuevo_registro)
        }
