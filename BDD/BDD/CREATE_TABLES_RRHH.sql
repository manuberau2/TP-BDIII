USE RecursosHumanos;
GO

BEGIN TRANSACTION;
-- Tabla: Locales
CREATE TABLE Locales (
    id_local      INT PRIMARY KEY,
    nombre_local  VARCHAR(100) NOT NULL,
    direccion     VARCHAR(150),
    ciudad        VARCHAR(100),
    provincia     VARCHAR(100)
);

-- Tabla: Empleado
CREATE TABLE Empleado (
    legajo         INT PRIMARY KEY,
    nombre         VARCHAR(100) NOT NULL,
    apellido       VARCHAR(100) NOT NULL,
    direccion      VARCHAR(150),
    sueldo         DECIMAL(18,2),
    fecha_ingreso  DATE,
    id_local       INT,
    FOREIGN KEY (id_local) REFERENCES Locales(id_local)
);

-- Tabla: Telefono_empleado
CREATE TABLE TelefonoEmpleado (
    legajo             INT NOT NULL,
    telefono_empleado  VARCHAR(20) NOT NULL,
    PRIMARY KEY (legajo, telefono_empleado),
    FOREIGN KEY (legajo) REFERENCES Empleado(legajo)
);

-- Tabla: Capacitacion
CREATE TABLE Capacitacion (
    id_capacitacion   INT PRIMARY KEY,
    descripcion       VARCHAR(150) NOT NULL,
    duracion_horas    INT NOT NULL,
    fecha_inicio      DATE,
    franja_horaria    VARCHAR(30) NOT NULL
);

-- Tabla: CapacitacionXEmpleado
CREATE TABLE CapacitacionXEmpleado (
    id_capacitacion   INT NOT NULL,
    legajo            INT NOT NULL,
    resultado         VARCHAR(50),
    PRIMARY KEY (id_capacitacion, legajo),
    FOREIGN KEY (id_capacitacion) REFERENCES Capacitacion(id_capacitacion),
    FOREIGN KEY (legajo) REFERENCES Empleado(legajo)
);

-- Tabla: Motivo_Ausencia
CREATE TABLE MotivoAusencia (
    cod_motivo     INT PRIMARY KEY,
    descripcion    VARCHAR(100) NOT NULL
);

-- Tabla: Empleado_ausencia
CREATE TABLE EmpleadoAusencia (
    legajo           INT NOT NULL,
    fecha_ausencia   DATE NOT NULL,
    cod_motivo       INT NOT NULL,
    PRIMARY KEY (legajo, fecha_ausencia),
    FOREIGN KEY (legajo) REFERENCES Empleado(legajo),
    FOREIGN KEY (cod_motivo) REFERENCES MotivoAusencia(cod_motivo)
);

-- Tabla: Categoria
CREATE TABLE Categoria (
    id_categoria_salarial   INT PRIMARY KEY,
    descripcion           VARCHAR(100) NOT NULL
);

-- Tabla: BasicoCategoria
CREATE TABLE BasicoCategoria (
    id_categoria_salarial   INT NOT NULL,
    fecha_inicio_vigencia   DATE NOT NULL,
    fecha_fin_vigencia      DATE,
    salario_basico         DECIMAL(18,2) NOT NULL,
    PRIMARY KEY (id_categoria_salarial, fecha_inicio_vigencia),
    FOREIGN KEY (id_categoria_salarial) REFERENCES Categoria(id_categoria_salarial)
);

-- Tabla: CategoriaXEmpleado
CREATE TABLE CategoriaEmpleado (
    id_categoria_salarial   INT NOT NULL,
    legajo                INT NOT NULL,
    fecha_inicio           DATE NOT NULL,
    fecha_fin              DATE,
    PRIMARY KEY (id_categoria_salarial, legajo, fecha_inicio),
    FOREIGN KEY (id_categoria_salarial) REFERENCES Categoria(id_categoria_salarial),
    FOREIGN KEY (legajo) REFERENCES Empleado(legajo)
);

COMMIT;