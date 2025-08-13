from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Dict, Any, Optional

# --- Importaciones de nuestra arquitectura ---
from app.database.database import get_db
from app.services import report_service
from app.services import sheet_service # <-- Asegúrate que el nombre del servicio es correcto
from app.core.security import verify_firebase_token
from app.schemas import esquemas as schemas 

router = APIRouter()

# --- Endpoint GET existente (para ver el reporte en la app) ---
@router.get("/attendance", response_model=List[Dict[str, Any]])
def get_attendance_report(
    report_date: date,
    cost_center: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Obtiene el reporte de asistencias para una fecha específica.
    """
    report_data = report_service.get_daily_attendance_report(
        db=db,
        report_date=report_date,
        cost_center=cost_center
    )
    return report_data


# --- Endpoint POST para exportar (versión FastAPI) ---
@router.post("/export-to-sheets", status_code=status.HTTP_200_OK)
def export_report_to_google_sheets(
    payload: schemas.ReportExportPayload,
    authorization: Optional[str] = Header(None)
):
    # 1. Autenticación (sin cambios)
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header no válido")
    try:
        token = authorization.split("Bearer ")[1]
        decoded_token = verify_firebase_token(token)
        user_email = decoded_token.get("email")
        if not user_email:
            raise HTTPException(status_code=403, detail="El token no contiene un email válido.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token inválido: {e}")

    # 2. Llamada al servicio
    try:
        # --- INICIO DE LA CORRECCIÓN ---
        # ID de la carpeta de Google Drive actualizado.
        DRIVE_FOLDER_ID = "1i9n4W7ysKJTZ1rpRWXVRYR9NYANvhZhZ"
        # --- FIN DE LA CORRECCIÓN ---

        file_title = f"Reporte de Asistencia - {payload.report_date.strftime('%Y-%m-%d')}"
        
        sheet_url = sheet_service.create_and_write_spreadsheet(
            report_data=payload.report_data,
            file_title=file_title,
            user_email=user_email,
            folder_id=DRIVE_FOLDER_ID # <-- Pasamos el nuevo parámetro
        )
        
        return {
            "message": "Nuevo reporte creado y exportado a Google Sheets con éxito.",
            "sheet_url": sheet_url
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

