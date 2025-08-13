# ===============================================================
# ARCHIVO: app/services/user_service.py (CORREGIDO)
# PROPÓSITO: Contiene la lógica de negocio para CREAR un nuevo
#            usuario con su plantilla de huella dactilar.
# ===============================================================
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models import tablas as models

def create_user_with_fingerprint(
    db: Session,
    numero_empleado: str,
    nombre_completo: str,
    departamento: int, # TIPO CORREGIDO: Es un entero (ID).
    huella_datos: str
):
    """
    Crea un nuevo usuario en la base de datos y le asigna
    inmediatamente su plantilla de huella.
    """
    # 1. Verificar si el departamento al que se asignará el usuario realmente existe.
    db_departamento = db.query(models.Departamento).filter(models.Departamento.id_departamento == departamento).first()
    if not db_departamento:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El departamento con ID {departamento} no fue encontrado."
        )

    # 2. Crear la nueva instancia del usuario con los campos correctos.
    nuevo_usuario = models.Usuario(
        numero_empleado=numero_empleado,
        nombre_completo=nombre_completo,
        # AÑADIDO: Campo de email requerido por el modelo. Ajústalo a tus necesidades.
        email=f"{numero_empleado}@ejemplo.com", 
        # SOLUCIÓN: Asigna el ID del departamento al campo de clave foránea `id_departamento`.
        id_departamento=departamento,
        # La columna 'plantilla_huella' es de tipo BLOB, por lo que convertimos el string a bytes.
        plantilla_huella=huella_datos.encode('utf-8')
    )

    # 3. Guardar en la base de datos con manejo de errores de integridad.
    try:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
    except IntegrityError:
        db.rollback() # Revierte la transacción en caso de error
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Ya existe un empleado con el número '{numero_empleado}' o el email."
        )

    print(f"--- Nuevo usuario CREADO con huella. Número: {nuevo_usuario.numero_empleado} ---")
    return nuevo_usuario