# ===============================================================
# ARCHIVO: app/services/report_service.py (CORREGIDO)
# PROPÓSITO: Contiene ÚNICAMENTE la lógica de negocio para generar
#            el reporte de asistencias.
# ===============================================================
from sqlalchemy.orm import Session, joinedload
from datetime import date, datetime
from typing import Optional

from app.models import tablas as models

def get_daily_attendance_report(db: Session, report_date: date, cost_center: Optional[str] = None):
    """
   genarando reporte 
    """
    print(f"\n--- Iniciando reporte de asistencia para la fecha: {report_date} ---")
    if cost_center:
        print(f"--- Recibido parámetro de Cost Center: {cost_center} ---")

    PRIVILEGED_COST_CENTERS = {'C003', 'CC_RH_01'}

    report = []

    query_users = db.query(models.Usuario).options(
        joinedload(models.Usuario.departamento),
        joinedload(models.Usuario.rol)
    )

    if cost_center is not None and cost_center not in PRIVILEGED_COST_CENTERS:
        print(f"--- Aplicando filtro para el Cost Center: {cost_center} ---")
        query_users = query_users.filter(models.Usuario.costCenter == cost_center)
    else:
        print("--- No se aplica filtro de Cost Center. Mostrando todos los usuarios. ---")
    
    users = query_users.all()
    print(f"--- Encontrados {len(users)} usuarios para procesar. ---")

    for user in users:
        assignment = db.query(models.AsignacionHorario).options(
            joinedload(models.AsignacionHorario.tipo_horario)
        ).filter(
            models.AsignacionHorario.id_usuario == user.id_usuario,
            models.AsignacionHorario.fecha == report_date
        ).first()
        
        attendance_record = db.query(models.RegistroAsistencia).filter(
            models.RegistroAsistencia.id_usuario == user.id_usuario,
            models.RegistroAsistencia.fecha == report_date
        ).first()

        status = "Sin Asignación"
        scheduled_check_in = None
        actual_check_in = None
        delay_minutes = 0

        if assignment and assignment.tipo_horario:
            scheduled_check_in = assignment.tipo_horario.hora_entrada
            status = "Ausencia"

        if attendance_record:
            actual_check_in = attendance_record.hora_entrada.time()
            status = "Asistencia"
            if scheduled_check_in:
                scheduled_dt = datetime.combine(report_date, scheduled_check_in)
                actual_dt = attendance_record.hora_entrada.replace(tzinfo=None)
                
                if actual_dt > scheduled_dt:
                    delay = actual_dt - scheduled_dt
                    delay_minutes = int(delay.total_seconds() / 60)
                    if delay_minutes > 5:
                        status = "Retardo"

        report_entry = {
            "user_id": user.id_usuario,
            "employee_number": user.numero_empleado,
            "full_name": user.nombre_completo,
            "department": user.departamento.nombre_depto if user.departamento else "N/A",
            "role": user.rol.nombre_rol if user.rol else "N/A",
            "cost_center": user.costCenter if user.costCenter else "N/A",
            "date": report_date.isoformat(),
            "scheduled_check_in": scheduled_check_in.strftime('%H:%M:%S') if scheduled_check_in else "N/A",
            "actual_check_in": actual_check_in.strftime('%H:%M:%S') if actual_check_in else "N/A",
            "check_out": attendance_record.hora_salida.strftime('%H:%M:%S') if attendance_record and attendance_record.hora_salida else "N/A",
            "status": status,
            "delay_minutes": delay_minutes
        }
        
        report.append(report_entry)

    print("\n--- Reporte finalizado. ---")
    return report