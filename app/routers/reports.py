from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Dict, Any, Optional
from app.core.security import verify_firebase_token
# Usamos las rutas de importación correctas basadas en tu proyecto
from app.database.database import get_db
from app.services import report_service
from app.schemas import esquemas as schemas 
from app.routers import sheets

router = APIRouter()

@router.get("/attendance", response_model=List[Dict[str, Any]], tags=["Reportes"])
def get_attendance_report(
    report_date: date,
    cost_center: Optional[str] = None, # <- 1. Cambiamos department_id por cost_center (usando str)
    db: Session = Depends(get_db)
):
    """
    Obtiene el reporte de asistencias para una fecha específica,
    con opción de filtrar por centro de costos (costCenter).

    Ejemplos de uso:
    - /reports/attendance?report_date=2025-07-31
    - /reports/attendance?report_date=2025-07-31&cost_center=CC_VENTAS_01
    """
    # 2. Pasamos el nuevo parámetro al servicio
    report_data = report_service.get_daily_attendance_report(
        db=db,
        report_date=report_date,
        cost_center=cost_center
    )
    return report_data

@router.post("/export-to-sheets", status_code=status.HTTP_200_OK)
def export_report_to_google_sheets(
    payload: schemas.ReportExportPayload, # Usa el nuevo esquema para validar el body
    authorization: Optional[str] = Header(None) # Obtiene el token del header
):
    """
    Recibe los datos de un reporte, CREA un nuevo archivo de Google Sheets,
    escribe los datos y lo comparte con el usuario autenticado.
    """
    # 1. Validar el token y obtener el email del usuario
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization header no válido")

    try:
        token = authorization.split("Bearer ")[1]
        decoded_token = verify_firebase_token(token)
        user_email = decoded_token.get("email")
        if not user_email:
            raise HTTPException(status_code=403, detail="El token no contiene un email válido.")
        print(f"Token de Firebase verificado con éxito para el usuario: {user_email}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token inválido: {e}")

    # 2. Llamar al servicio para CREAR Y ESCRIBIR en la hoja de cálculo
    try:
        # Título que tendrá el nuevo archivo en Google Drive
        file_title = f"Reporte de Asistencia - {payload.report_date.strftime('%Y-%m-%d')}"

        print(f"Iniciando la creación del archivo '{file_title}'...")

        sheet_url = sheets.create_and_write_spreadsheet(
            report_data=payload.report_data,
            file_title=file_title,
            user_email=user_email # Pasamos el email para compartir el archivo
        )

        return {
            "message": "Nuevo reporte creado y exportado a Google Sheets con éxito.",
            "sheet_url": sheet_url
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )