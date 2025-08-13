# app/services/vision_service.py
import base64
from fastapi import HTTPException, status
from google.cloud import vision
from ..core.clients import vision_client

def detect_face_from_base64(image_base64: str) -> vision.FaceAnnotation:
    """
    Recibe una imagen en Base64, la envía a Google Vision y devuelve la
    anotación del rostro si se detecta con suficiente confianza.
    Lanza una excepción HTTPException si falla la verificación.
    """
    if not vision_client:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="El cliente de Google Cloud Vision no está inicializado."
        )

    try:
        if ',' in image_base64:
            _, image_data = image_base64.split(',', 1)
        else:
            image_data = image_base64

        image_content = base64.b64decode(image_data)
        image = vision.Image(content=image_content)

        print("Enviando imagen a Google Cloud Vision para análisis...")
        response = vision_client.face_detection(image=image)
        
        if response.error.message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error de la API de Vision: {response.error.message}"
            )

        face_annotations = response.face_annotations
        if not face_annotations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se detectó ningún rostro en la imagen."
            )

        first_face = face_annotations[0]
        if first_face.detection_confidence < 0.90:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No se pudo verificar el rostro con suficiente confianza."
            )
        
        print(f"Rostro detectado con una confianza de: {first_face.detection_confidence:.2f}")
        return first_face

    except Exception as e:
        # Si ya es una HTTPException, relánzala. Si no, crea una nueva.
        if isinstance(e, HTTPException):
            raise e
        print(f"Error inesperado en el servicio de visión: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error interno al procesar la imagen."
        )