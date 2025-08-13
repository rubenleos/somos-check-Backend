# ===============================================================
# ARCHIVO: app/models/tablas.py
# PROPÓSITO: Define las tablas de la base de datos como clases de Python
#            usando SQLAlchemy. Es la "fuente de verdad" de tu
#            estructura de datos.
# ===============================================================
from sqlalchemy import (Column, Integer, String, ForeignKey, BLOB, TEXT,
                        UniqueConstraint, TIME, DATE, DATETIME, DECIMAL)
from sqlalchemy.orm import relationship
from ..database.database import Base

# --- Tabla 1: Roles ---
class Rol(Base):
    __tablename__ = "Roles"
    id_rol = Column(Integer, primary_key=True)
    nombre_rol = Column(String(50), unique=True, nullable=False, index=True)
    # Relación Inversa: Un rol puede tener muchos usuarios.
    usuarios = relationship("Usuario", back_populates="rol")

# --- Tabla 2: Departamentos ---
class Departamento(Base):
    __tablename__ = "Departamentos"
    id_departamento = Column(Integer, primary_key=True)
    nombre_depto = Column(String(100), unique=True, nullable=False, index=True)
    # Relación Inversa: Un departamento puede tener muchos usuarios.
    usuarios = relationship("Usuario", back_populates="departamento")

# --- Tabla 4: Tipos de Horario (Turnos) ---
class TipoHorario(Base):
    __tablename__ = "TiposHorario"
    id_tipo_horario = Column(Integer, primary_key=True)
    nombre_turno = Column(String(100), nullable=False)
    hora_entrada = Column(TIME, nullable=False)
    hora_salida = Column(TIME, nullable=False)
    # Relación Inversa: Un tipo de horario puede estar en muchas asignaciones.
    asignaciones = relationship("AsignacionHorario", back_populates="tipo_horario")

# --- Tabla 3: Usuarios ---
class Usuario(Base):
    __tablename__ = "Usuarios"
    id_usuario = Column(Integer, primary_key=True)
    numero_empleado = Column(String(20), unique=True, nullable=False, index=True)
    nombre_completo = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    google_id = Column(String(255), unique=True, nullable=True) # Reutilizado para el UID de Firebase
    plantilla_huella = Column(BLOB, nullable=True)
    plantilla_facial = Column(TEXT, nullable=True)
    costCenter = Column(String(4), nullable=True)
    # Llaves Foráneas
    id_rol = Column(Integer, ForeignKey("Roles.id_rol"), nullable=True)
    id_departamento = Column(Integer, ForeignKey("Departamentos.id_departamento"), nullable=True)
    # Relaciones Directas (El lado "muchos" de la relación)
    rol = relationship("Rol", back_populates="usuarios")
    departamento = relationship("Departamento", back_populates="usuarios")
    # Relaciones Inversas (El lado "uno" de la relación)
    asignaciones = relationship("AsignacionHorario", back_populates="usuario", cascade="all, delete-orphan")
    registros_asistencia = relationship("RegistroAsistencia", back_populates="usuario", cascade="all, delete-orphan")
    eventos_adicionales = relationship("EventoAdicional", back_populates="usuario", cascade="all, delete-orphan")
    
# --- Tabla 5: Asignación de Horarios ---
class AsignacionHorario(Base):
    __tablename__ = "AsignacionesHorario"
    id_asignacion = Column(Integer, primary_key=True)
    fecha = Column(DATE, nullable=False)
    # Llaves Foráneas
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=False)
    id_tipo_horario = Column(Integer, ForeignKey("TiposHorario.id_tipo_horario"), nullable=False)
    # Relaciones Directas
    usuario = relationship("Usuario", back_populates="asignaciones")
    tipo_horario = relationship("TipoHorario", back_populates="asignaciones")
    # Restricción Única
    __table_args__ = (UniqueConstraint('id_usuario', 'fecha', name='_usuario_fecha_uc'),)

# --- Tabla 6: Registros de Asistencia ---
class RegistroAsistencia(Base):
    __tablename__ = "RegistrosAsistencia"
    numero_empleado = Column(String(20), nullable=False, index=True)
    id_registro = Column(Integer, primary_key=True)
    fecha = Column(DATE, nullable=False) # Se podría derivar de hora_entrada pero tenerla explícita es útil para queries
    hora_entrada = Column(DATETIME, nullable=False)
    hora_salida = Column(DATETIME, nullable=True)
    # Llave Foránea
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=False)
    # Relación Directa
    usuario = relationship("Usuario", back_populates="registros_asistencia")

# --- Tabla 7: Eventos Adicionales ---
class EventoAdicional(Base):
    __tablename__ = "EventosAdicionales"
    id_evento = Column(Integer, primary_key=True)
    tipo_evento = Column(String(20), nullable=False)
    fecha_inicio = Column(DATE, nullable=False)
    fecha_fin = Column(DATE, nullable=True)
    horas_solicitadas = Column(DECIMAL(4, 2), nullable=True)
    motivo = Column(TEXT, nullable=True)
    estado = Column(String(20), nullable=False, default='PENDIENTE')
    # Llave Foránea
    id_usuario = Column(Integer, ForeignKey("Usuarios.id_usuario"), nullable=False)
    # Relación Directa
    usuario = relationship("Usuario", back_populates="eventos_adicionales")
