# app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.core.security import verify_firebase_token
from app.services import user_service, face_service # Asumimos que el alta facial crea el usuario
from app.models import tablas as models
from app.schemas import esquemas as schemas

router = APIRouter()

# --- Modelos de Petición (Payloads) ---
class EnrollFacePayload(BaseModel):
    image_base64: str
    firebase_token: str
    numero_empleado: str
    nombre_completo: str
    email: EmailStr

# --- Endpoint de Alta Facial ---
@router.post("/enroll-face", response_model=schemas.Usuario, status_code=status.HTTP_201_CREATED)
def alta_facial(payload: EnrollFacePayload, db: Session = Depends(get_db)):
    """
    Crea un nuevo usuario en el sistema y le asigna su plantilla facial.
    La operación es validada por el token de un administrador/operador.
    """
    # 1. Verificamos que quien hace la petición esté autenticado vía Firebase.
    verify_firebase_token(payload.firebase_token)

    # 2. Generamos el embedding facial a partir de la imagen
    embedding_facial_json = face_service.generate_embedding(payload.image_base64)

    # 3. Verificamos si el usuario ya existe
    usuario_existente = db.query(models.Usuario).filter(
        (models.Usuario.numero_empleado == payload.numero_empleado) | (models.Usuario.email == payload.email)
    ).first()
    if usuario_existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un empleado con ese número o email.")

    # 4. Creamos el nuevo usuario con su plantilla facial
    nuevo_usuario = models.Usuario(
        numero_empleado=payload.numero_empleado,
        nombre_completo=payload.nombre_completo,
        email=payload.email,
        plantilla_facial=embedding_facial_json
    )
    
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario