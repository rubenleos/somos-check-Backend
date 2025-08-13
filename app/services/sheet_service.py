import os
import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# --- Permisos requeridos ---
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials_oauth.json")
def _get_gspread_client():
    """
    verifico si el token esta funcionando @
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return gspread.authorize(creds), creds


def create_and_write_spreadsheet(report_data, file_title, user_email, folder_id=None):
    """
    Crea un archivo de Google Sheets en la carpeta indicada y escribe los datos.
    
    :param report_data: Lista de diccionarios con los datos a exportar.
    :param file_title: Título del archivo.
    :param user_email: Email del usuario que solicita la exportación (no se usa en OAuth directo, pero puedes usarlo para logging).
    :param folder_id: ID de carpeta de Google Drive donde se guardará el archivo.
    """
    client, creds = _get_gspread_client()

    # --- Crear archivo en Drive ---
    drive_service = build("drive", "v3", credentials=creds)
    file_metadata = {
        "name": file_title,
        "mimeType": "application/vnd.google-apps.spreadsheet"
    }
    if folder_id:
        file_metadata["parents"] = [folder_id]

    file = drive_service.files().create(body=file_metadata).execute()
    spreadsheet_id = file.get("id")

    # --- Escribir datos en el Sheet ---
    sheet = client.open_by_key(spreadsheet_id)
    worksheet = sheet.get_worksheet(0)

    if report_data:
        # Escribir encabezados
        headers = list(report_data[0].keys())
        worksheet.insert_row(headers, 1)

        # Escribir filas
        for row in report_data:
            worksheet.append_row(list(row.values()))

    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
