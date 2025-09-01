# Pydantic v2
from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserOut(BaseModel):
    id_usuario: int
    numero_empleado: str
    nombre_completo: str
    email: str
    id_departamento: int
    # Para el endpoint simple (sin JOIN) esto puede no venir; lo dejamos opcional
    nombre_depto: Optional[str] = None

    # <- importantísimo en v2 para mapear desde SQLAlchemy
    model_config = ConfigDict(from_attributes=True)


class UserWithDeptOut(BaseModel):
    id_usuario: int
    numero_empleado: str
    nombre_completo: str
    email: str
    id_departamento: int
    nombre_depto: str