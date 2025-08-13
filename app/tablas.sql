

CREATE TABLE Roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE Departamentos (
    id_departamento INT AUTO_INCREMENT PRIMARY KEY,
    nombre_depto VARCHAR(100) NOT NULL UNIQUE
);
CREATE TABLE Usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    numero_empleado VARCHAR(20) NOT NULL UNIQUE,
    nombre_completo VARCHAR(150) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,      -- CAMBIO: Añadido para el login
    google_id VARCHAR(255) UNIQUE,           -- CAMBIO: Añadido, para el ID único de Google
    -- password_hash VARCHAR(255) NOT NULL,   -- CAMBIO: Eliminado
    id_rol INT,
    id_departamento INT,
    plantilla_huella BLOB,
    plantilla_facial TEXT,

    FOREIGN KEY (id_rol) REFERENCES Roles(id_rol) ON DELETE SET NULL,
    FOREIGN KEY (id_departamento) REFERENCES Departamentos(id_departamento) ON DELETE SET NULL
);

CREATE TABLE TiposHorario (
    id_tipo_horario INT AUTO_INCREMENT PRIMARY KEY,
    nombre_turno VARCHAR(100) NOT NULL,
    hora_entrada TIME NOT NULL,
    hora_salida TIME NOT NULL
);

-- ========= TABLA 5: Asignación de Horarios por Día (Soluciona el horario rotativo) =========
CREATE TABLE AsignacionesHorario (
    id_asignacion INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_tipo_horario INT NOT NULL,
    fecha DATE NOT NULL,
    -- Un usuario no puede tener dos turnos asignados el mismo día
    UNIQUE (id_usuario, fecha),
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE, -- Si se borra el usuario, se borran sus asignaciones.
    FOREIGN KEY (id_tipo_horario) REFERENCES TiposHorario(id_tipo_horario) ON DELETE CASCADE
);

-- ========= TABLA 6: Registros de Asistencia (Entradas y Salidas) =========
CREATE TABLE RegistrosAsistencia (
    id_registro INT AUTO_INCREMENT PRIMARY KEY,
    numero_empleado = Column(String(20), nullable=False, index=True),
    id_usuario INT NOT NULL,
    fecha DATE NOT NULL,
    hora_entrada DATETIME NOT NULL,
    hora_salida DATETIME, -- Permite nulo porque el usuario aún no ha checado su salida
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
);

-- ========= TABLA 7: Eventos Adicionales (Ausencias, Horas Extra, etc.) =========
CREATE TABLE EventosAdicionales (
    id_evento INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    tipo_evento VARCHAR(20) NOT NULL, -- 'AUSENCIA', 'HORAS EXTRA', 'VACACIONES', 'PERMISO'
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    horas_solicitadas DECIMAL(4, 2),
    motivo TEXT,
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE', -- 'PENDIENTE', 'APROBADO', 'RECHAZADO'
    FOREIGN KEY (id_usuario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
);