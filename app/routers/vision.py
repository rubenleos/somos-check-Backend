# ===============================================================
# ARCHIVO: app/routers/vision.py
# PROPÓSITO: Endpoint para el checador con reconocimiento facial.
# ===============================================================
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
# --- Importaciones de nuestra arquitectura ---
from ..database.database import get_db
from ..core.security import verify_firebase_token
from ..services import vision_service, attendance_service,face_service
from ..models import tablas as models
from ..schemas import esquemas as schemas
router = APIRouter()
# --- Modelo Pydantic para la Petición ---
class FaceCheckPayload(BaseModel):
    image_base64: str
    firebase_token: str

@router.post("/face-check", tags=["Checador Facial"])
def checador_facial(
    payload: FaceCheckPayload,
    db: Session = Depends(get_db)
):
    # 1. Autenticar al usuario (sin cambios)
    token_data = verify_firebase_token(payload.firebase_token)
    email = token_data.get("email")
    usuario = db.query(models.Usuario).filter(models.Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    # --- INICIO DE LA LÓGICA DE VERIFICACIÓN ---
    # 2. Comparamos el rostro de la foto actual con la plantilla guardada.
    coinciden = face_service.verify_faces_match(
        image_base64_check=payload.image_base64,
        stored_embedding_json=usuario.plantilla_facial
    )
    if not coinciden:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Verificación facial fallida. El rostro no coincide."
        )
    # --- FIN DE LA LÓGICA DE VERIFICACIÓN ---
    # 3. Si coinciden, registramos la asistencia (sin cambios)
    registro = attendance_service.register_attendance(db=db, user_id=usuario.id_usuario)    
    return {
        "verificado": True,
        "mensaje": registro["mensaje"],
        "registro": registro["data"]
    }
