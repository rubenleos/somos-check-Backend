# ===============================================================
# ARCHIVO: app/schemas/esquemas.py
# PROPÓSITO: Define la "forma" de los datos para la API usando Pydantic.
#            Valida los datos de entrada y formatea los de salida.
#            Separa la lógica de la API de la de la base de datos.
# ===============================================================
from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List,Dict,Any
from datetime import date, time, datetime

# --- Esquemas Base (para reusar) y de Creación ---
# Estos definen los campos necesarios para crear un nuevo registro.

class RolBase(BaseModel):
    nombre_rol: str

class RolCreate(RolBase):
    pass # No necesita campos adicionales para crear

class DepartamentoBase(BaseModel):
    nombre_depto: str

class DepartamentoCreate(DepartamentoBase):
    pass

class UsuarioBase(BaseModel):
    numero_empleado: str
    nombre_completo: str
    email: EmailStr # Pydantic validará que sea un formato de email válido

class UsuarioCreate(UsuarioBase):
    # El password no se incluye porque el login es con Google
    id_rol: Optional[int] = None
    id_departamento: Optional[int] = None

class TipoHorarioBase(BaseModel):
    nombre_turno: str
    hora_entrada: time
    hora_salida: time

class TipoHorarioCreate(TipoHorarioBase):
    pass

class AsignacionHorarioBase(BaseModel):
    id_usuario: int
    id_tipo_horario: int
    fecha: date

class AsignacionHorarioCreate(AsignacionHorarioBase):
    pass

class RegistroAsistenciaBase(BaseModel):
    numero_empleado: str
    id_usuario: int
    fecha: date
    hora_entrada: datetime
    hora_salida: Optional[datetime] = None

class RegistroAsistenciaCreate(BaseModel):
    # Al crear un check-in, solo se necesitan estos datos
    id_usuario: int
    hora_entrada: datetime
    fecha: date

class RegistroAsistenciaUpdate(BaseModel):
    # Para hacer el check-out, solo actualizamos la hora de salida
    hora_salida: datetime

class EventoAdicionalBase(BaseModel):
    id_usuario: int
    tipo_evento: str
    fecha_inicio: date
    fecha_fin: Optional[date] = None
    horas_solicitadas: Optional[float] = None # Pydantic maneja Decimal como float
    motivo: Optional[str] = None

class EventoAdicionalCreate(EventoAdicionalBase):
    pass

class EventoAdicionalUpdate(BaseModel):
    # Para que un admin apruebe o rechace una solicitud
    estado: str 

# --- Esquemas de Respuesta (lo que la API devuelve al cliente) ---
# Usan `ConfigDict(from_attributes=True)` para ser compatibles con los modelos de SQLAlchemy

class Rol(RolBase):
    id_rol: int
    model_config = ConfigDict(from_attributes=True)

class Departamento(DepartamentoBase):
    id_departamento: int
    model_config = ConfigDict(from_attributes=True)

class TipoHorario(TipoHorarioBase):
    id_tipo_horario: int
    model_config = ConfigDict(from_attributes=True)

# Esquema de Usuario simplificado para evitar bucles infinitos en las relaciones
class UsuarioSimple(UsuarioBase):
    id_usuario: int
    model_config = ConfigDict(from_attributes=True)

# Esquema de Usuario completo con sus relaciones
class Usuario(UsuarioBase):
    id_usuario: int
    rol: Optional[Rol] = None
    departamento: Optional[Departamento] = None
    model_config = ConfigDict(from_attributes=True)

class AsignacionHorario(AsignacionHorarioBase):
    id_asignacion: int
    usuario: UsuarioSimple # Anidamos la info del usuario
    tipo_horario: TipoHorario # Anidamos la info del turno
    model_config = ConfigDict(from_attributes=True)

class RegistroAsistencia(RegistroAsistenciaBase):
    id_registro: int
    model_config = ConfigDict(from_attributes=True)

class EventoAdicional(EventoAdicionalBase):
    id_evento: int
    estado: str
    model_config = ConfigDict(from_attributes=True)

class UsuarioAdmin(Usuario):
    tiene_plantilla_facial: bool = False   

class ReportExportPayload(BaseModel):
    report_date: date
    report_data: List[Dict[str, Any]]     
