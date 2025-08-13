# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- Importaciones de nuestra arquitectura ---
from app.database.database import Base, engine
# Importamos solo los routers que necesitamos y que ahora están limpios
from app.routers import admin, auth, gestion, vision, fingerprint, asistencia,reports,department,sheets # Asumo que tienes asistencia.py

# --- Creación de las tablas en la base de datos ---
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API de Checador y Control de Asistencia",
    description="Backend para gestionar la asistencia de empleados con FastAPI.",
    version="1.0.0"
)

# --- Middleware de CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- REGISTRO DE TODOS LOS ROUTERS ---
app.include_router(auth.router, prefix="/auth", tags=["Autenticación"])
app.include_router(admin.router, prefix="/admin", tags=["Administración"])
app.include_router(gestion.router, prefix="/gestion", tags=["Gestión Administrativa"])
app.include_router(vision.router, prefix="/vision", tags=["Checador Facial"])
app.include_router(asistencia.router, prefix="/asistencia", tags=["Asistencia (Checador)"])
app.include_router(reports.router, prefix="/reports", tags=["Reportes"])
app.include_router(department.router, prefix="/departments", tags=["Departamentos"]);
app.include_router(sheets.router,prefix="/sheets", tags=["Departamentos"])

# --- AQUÍ ESTÁ LA LÍNEA CLAVE ---
# Añadimos nuestro router de huellas unificado.
app.include_router(fingerprint.router) # El prefijo ya está definido en el propio router


@app.get("/", tags=["Health Check"])
def health_check():
    """
    Endpoint raíz para verificar que la API está funcionando.
    """
    return {"status": "ok", "message": "¡Bienvenido a la API del Checador!"}