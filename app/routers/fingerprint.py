# app/routers/fingerprint.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.security import verify_firebase_token
from app.models import tablas as models
from app.schemas import esquemas as schemas
from app.services import attendance_service, user_service

# --- Router Principal para Huellas ---
router = APIRouter(
    prefix="/fingerprint",  # Todas las rutas aquí comenzarán con /fingerprint
    tags=["Huella Digital"]
)

# --- Modelos de Petición (Payloads) ---
class EnrollFingerprintPayload(BaseModel):
    firebase_token: str
    numero_empleado: str
    nombre_completo: str
    departamento: int
    
    huella_datos: str # La plantilla de la huella en formato texto/XML

class AddFingerprintPayload(BaseModel):
    firebase_token: str
    numero_empleado: str
    huella_datos: str

class AttendancePayload(BaseModel):
    numero_empleado: str

# --- Endpoints Consolidados ---

@router.post("/enroll", response_model=schemas.Usuario, status_code=status.HTTP_201_CREATED)
def enroll_user_with_fingerprint(payload: EnrollFingerprintPayload, db: Session = Depends(get_db)):
    """
    Crea un nuevo empleado en el sistema JUNTO CON su plantilla de huella.
    Esta es la forma principal de enrolar con huella.
    """
    verify_firebase_token(payload.firebase_token)
    
    # Usamos el servicio que ya tenías para mantener la lógica de negocio separada
    nuevo_usuario = user_service.create_user_with_fingerprint(
        db=db,
        numero_empleado=payload.numero_empleado,
        nombre_completo=payload.nombre_completo,
        departamento=payload.departamento,
        huella_datos=payload.huella_datos
    )
    return nuevo_usuario

@router.get("/template/{numero_empleado}", response_model=dict)
def get_fingerprint_template(numero_empleado: str, db: Session = Depends(get_db)):
    """
    Busca un empleado por su número y devuelve su plantilla de huella guardada.
    ¡ESTA ES LA RUTA QUE DEBES USAR AHORA PARA TU GET!
    """
    print(f"Buscando plantilla para el empleado: {numero_empleado}")
    usuario = db.query(models.Usuario).filter(models.Usuario.numero_empleado == numero_empleado).first()

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail=f"Empleado con número {numero_empleado} no encontrado."
        )

    if not usuario.plantilla_huella:
        raise HTTPException(
            status_code=404,
            detail=f"El empleado {numero_empleado} no tiene una huella registrada."
        )

    # El tipo BLOB de la BD se devuelve como bytes, lo decodificamos a string
    # para que sea un JSON válido y el cliente lo pueda usar.
    print(f"--> Plantilla encontrada para {numero_empleado}. Enviando al cliente.")
    return {"huella_template": usuario.plantilla_huella.decode('utf-8')}



@router.post("/record-attendance")
def record_attendance_after_verification(payload: AttendancePayload, db: Session = Depends(get_db)):
    """
    Busca al empleado y registra su entrada o salida.
    """
    usuario = db.query(models.Usuario).filter(models.Usuario.numero_empleado == payload.numero_empleado).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Empleado no encontrado al registrar asistencia.")

    # --- CAMBIO: Pasamos el objeto 'usuario' completo ---
    registro = attendance_service.register_attendance(db=db, usuario=usuario)
    
    return {
        "verificado": True,
        "mensaje": registro["mensaje"],
        "registro": registro["data"]
    }
