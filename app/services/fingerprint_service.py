# ===============================================================
# ARCHIVO: app/services/fingerprint_service.py
# PROPÓSITO: Contiene la lógica para verificar si una huella
#            capturada coincide con una almacenada.
# ===============================================================
from fastapi import HTTPException, status

def verify_fingerprints_match(
    captured_fingerprint_data: str,
    stored_fingerprint_template: bytes
) -> bool:
    """
    Compara los datos de una huella capturada con la plantilla guardada.
    """
    if not stored_fingerprint_template:
        raise HTTPException(
            status_code=400,
            detail="El usuario no tiene una huella dactilar registrada."
        )

    # Convertimos la plantilla guardada (bytes) de nuevo a string para comparar.
    stored_fingerprint_str = stored_fingerprint_template.decode('utf-8')

    # La verificación es una comparación directa de las plantillas.
    # Si el lector y el software son los mismos, las plantillas deben coincidir.
    if captured_fingerprint_data == stored_fingerprint_str:
        print("--- Verificación de huella exitosa: Las plantillas coinciden. ---")
        return True
    else:
        print("--- Verificación de huella fallida: Las plantillas NO coinciden. ---")
        return False
