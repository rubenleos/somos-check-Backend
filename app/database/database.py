# ===============================================================
# ARCHIVO: app/database.py (Configurado para MySQL)
# PROPÓSITO: Establece la conexión con la base de datos MySQL.
# ===============================================================
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# --- Configuración de la Conexión a MySQL ---
# Lee las variables de entorno o usa valores por defecto.
# Es una mejor práctica no escribir contraseñas directamente en el código.
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Maycodb!2016") # <-- ¡CAMBIA ESTO!
DB_HOST = os.getenv("DB_HOST", "192.168.6.30") # O la IP de tu servidor de BD
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "checkuser_db") # El nombre de tu base de datos en MySQL

# String de conexión para MySQL con el driver PyMySQL
SQLALCHEMY_DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# --- INICIO DE LA CORRECCIÓN ---
# Se añade el parámetro 'pool_pre_ping=True'.
# Esto le dice a SQLAlchemy que verifique la conexión antes de usarla,
# lo que evita los errores de "MySQL server has gone away".
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True
)
# --- FIN DE LA CORRECCIÓN ---

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependencia para obtener la sesión de la base de datos en cada endpoint
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

