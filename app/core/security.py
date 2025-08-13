# ===============================================================
# ARCHIVO: app/core/security.py (Actualizado para Firebase)
# PROPÓSITO: Maneja la lógica de autenticación, incluyendo la
#            verificación de tokens y la creación de sesiones.
# ===============================================================
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from typing import Optional
import os

# --- Importaciones para Firebase ---
import firebase_admin
from firebase_admin import credentials, auth

# --- CONFIGURACIÓN DE NUESTRO PROPIO TOKEN (JWT para la sesión) ---
# Esto no cambia. Sigue siendo el token para la sesión DENTRO de nuestra app.
SECRET_KEY = "Mayco250625developerrls"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8 # 8 horas

# --- INICIALIZACIÓN DE FIREBASE ADMIN ---
# La ruta al archivo de credenciales que descargaste.
# Se asume que está en la raíz del proyecto.
CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "firebase-credentials.json")

# Se inicializa la app de Firebase. El 'if' previene que se inicialice múltiples veces.
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate(CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK inicializado correctamente.")
    except Exception as e:
        print(f"ERROR: No se pudo inicializar Firebase Admin SDK. Revisa la ruta de tus credenciales: {e}")
        # En un entorno de producción, podrías querer que la app no inicie si esto falla.

def verify_firebase_token(token: str) -> dict:
    """
    Verifica un idToken de Firebase usando el SDK de Firebase Admin.
    Si el token es válido, devuelve los datos decodificados del usuario.
    Si no, lanza una excepción HTTPException.
    """
    try:
        # La función verify_id_token se encarga de todo:
        # - Verifica la firma y la expiración.
        # - Se comunica de forma segura con los servidores de Google.
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except auth.InvalidIdTokenError:
        # El token es inválido (mala firma, malformado, etc.)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de Firebase inválido.",
        )
    except auth.ExpiredIdTokenError:
        # El token ha expirado.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de Firebase expirado. Por favor, inicia sesión de nuevo.",
        )
    except Exception as e:
        # Cualquier otro error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ocurrió un error al verificar el token de Firebase: {e}",
        )


# --- Creación de nuestro token de sesión (sin cambios) ---
class TokenData(BaseModel):
    email: Optional[str] = None

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
