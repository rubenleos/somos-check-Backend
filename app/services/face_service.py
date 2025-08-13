# ===============================================================
# ARCHIVO: app/services/face_service.py
# PROPÓSITO: Contiene la lógica para generar "embeddings" faciales
#            y comparar rostros usando la librería deepface.
# ===============================================================
# ===============================================================
# ARCHIVO: app/services/face_service.py (con Logs de Depuración)
# ===============================================================
import base64
import json
import numpy as np
from deepface import DeepFace
from fastapi import HTTPException, status
import tempfile
import os

def _decode_image(image_base64: str) -> str:
    """Helper function to decode base64 image and save it temporarily."""
    
    # --- LOG 1: Imprimimos los primeros 100 caracteres de lo que recibimos ---
    print(f"--- LOG (face_service): Recibido image_base64 (primeros 100 chars): {image_base64[:100]}")

    try:
        if ',' in image_base64:
            print("--- LOG (face_service): Se detectó prefijo 'data:image...', limpiando la cadena.")
            _, image_data = image_base64.split(',', 1)
        else:
            print("--- LOG (face_service): No se detectó prefijo, usando la cadena como viene.")
            image_data = image_base64
        
        # --- LOG 2: Verificamos si la cadena tiene el padding correcto ---
        # A veces, el padding de base64 se pierde. Esto lo corrige.
        missing_padding = len(image_data) % 4
        if missing_padding:
            print(f"--- LOG (face_service): Corrigiendo padding. Añadiendo {4 - missing_padding} caracteres '='.")
            image_data += '=' * (4 - missing_padding)
            
        image_bytes = base64.b64decode(image_data)
        
        temp_dir = tempfile.gettempdir()
        temp_image_path = os.path.join(temp_dir, "temp_face_image.jpg")
        
        with open(temp_image_path, "wb") as f:
            f.write(image_bytes)
        
        print(f"--- LOG (face_service): Imagen guardada temporalmente en {temp_image_path}")
        return temp_image_path
        
    except Exception as e:
        # --- LOG 3: Si la decodificación falla, imprimimos el error ---
        print(f"--- ERROR (face_service): Falló la decodificación de Base64. Error: {e}")
        raise HTTPException(status_code=400, detail="Invalid base64 image format.")

def generate_embedding(image_base64: str) -> str:
    """
    Genera un embedding facial de una imagen y lo devuelve como un string JSON.
    """
    temp_image_path = _decode_image(image_base64)
    try:
        print("--- LOG (face_service): Llamando a DeepFace.represent...")
        embedding_objs = DeepFace.represent(img_path=temp_image_path, model_name='VGG-Face', enforce_detection=True)
        embedding = embedding_objs[0]['embedding']
        print("--- LOG (face_service): Embedding generado por DeepFace exitosamente.")
        return json.dumps(embedding)
    except ValueError as e:
        print(f"--- ERROR (face_service): DeepFace no detectó un rostro. Error: {e}")
        raise HTTPException(status_code=400, detail=f"No se pudo procesar el rostro: {e}")
    except Exception as e:
        print(f"--- ERROR (face_service): Error inesperado en DeepFace. Error: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno en el procesamiento facial: {e}")

# La función verify_faces_match no necesita logs adicionales por ahora,
# ya que el error ocurre antes.
def verify_faces_match(image_base64_check: str, stored_embedding_json: str) -> bool:
    # ... (código sin cambios)
    if not stored_embedding_json:
        raise HTTPException(status_code=400, detail="No hay una plantilla facial registrada para este usuario.")
    embedding_check_json = generate_embedding(image_base64_check)
    embedding_check = np.array(json.loads(embedding_check_json))
    stored_embedding = np.array(json.loads(stored_embedding_json))
    try:
        resultado = DeepFace.verify(
            img1_path=embedding_check, 
            img2_path=stored_embedding, 
            model_name='VGG-Face'
        )
        print(f"Resultado de la verificación facial: {resultado}")
        return resultado['verified']
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante la comparación facial: {e}")

