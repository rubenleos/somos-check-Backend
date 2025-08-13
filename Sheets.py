import os
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# --- Permisos ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_credentials():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials_oauth.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return creds

# --- Autenticación ---
creds = get_credentials()
client = gspread.authorize(creds)

# --- ID de carpeta de destino ---
FOLDER_ID = "1i9n4W7ysKJTZ1rpRWXVRYR9NYANvhZhZ"  # Cambia por tu carpeta

# --- Crear archivo en carpeta usando la API de Drive ---
drive_service = build("drive", "v3", credentials=creds)

file_metadata = {
    "name": "Mi Sheet en Carpeta Específica",
    "mimeType": "application/vnd.google-apps.spreadsheet",
    "parents": [FOLDER_ID]
}

file = drive_service.files().create(body=file_metadata).execute()
spreadsheet_id = file.get("id")

# --- Abrir con gspread y escribir ---
sheet = client.open_by_key(spreadsheet_id)
worksheet = sheet.get_worksheet(0)
worksheet.update_cell(1, 1, "Hola desde carpeta específica 🚀")

print(f"Archivo creado en carpeta: https://docs.google.com/spreadsheets/d/{spreadsheet_id}")
