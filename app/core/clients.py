# app/core/clients.py
import firebase_admin
from firebase_admin import credentials
from google.cloud import vision
import os

# --- Inicialización de Firebase Admin (Movido desde security.py) ---
try:
    CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "firebase-credentials.json")
    if not firebase_admin._apps:
        cred = credentials.Certificate(CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK inicializado correctamente.")
except Exception as e:
    print(f"ERROR: No se pudo inicializar Firebase Admin SDK: {e}")

# --- Inicialización de Google Cloud Vision ---
try:
    # Google Cloud Vision usará las mismas credenciales si están configuradas
    # a través de la variable de entorno GOOGLE_APPLICATION_CREDENTIALS.
    # Opcionalmente, puedes pasarle el mismo archivo de credenciales.
    vision_client = vision.ImageAnnotatorClient()
    print("Cliente de Google Cloud Vision inicializado correctamente.")
except Exception as e:
    vision_client = None
    print(f"ERROR: No se pudo inicializar el cliente de Vision: {e}")