USE FacturacionVentas;
GO

BEGIN TRANSACTION;

-- Tabla: Zona (nueva)
CREATE TABLE Zona (
    id_zona     INT PRIMARY KEY,
    nom_zona    VARCHAR(50) NOT NULL UNIQUE
);

-- Tabla: Provincia (modificada)
CREATE TABLE Provincia (
    id_provincia    INT PRIMARY KEY,
    nom_provincia   VARCHAR(100) NOT NULL UNIQUE,
    id_zona         INT NOT NULL,
    FOREIGN KEY (id_zona) REFERENCES Zona(id_zona)
);

CREATE TABLE Departamentos (
    id_depto     INT PRIMARY KEY,
    nom_depto    VARCHAR(100) NOT NULL,
    id_provincia INT NOT NULL,
    FOREIGN KEY (id_provincia) REFERENCES Provincia(id_provincia)
);

CREATE TABLE Ciudades (
    id_ciudad      INT PRIMARY KEY,
    id_depto       INT NOT NULL,
    nom_ciudad     VARCHAR(100) NOT NULL UNIQUE,
    poblacion      INT,
    clasificacion  VARCHAR(50),
    FOREIGN KEY (id_depto) REFERENCES Departamentos(id_depto)
);

CREATE TABLE Rubros (
    id_rubro    INT PRIMARY KEY,
    nom_rubro   VARCHAR(100) NOT NULL
);

CREATE TABLE Codigos (
    codigo       INT PRIMARY KEY,
    tipo         VARCHAR(30) NOT NULL,
    descripcion  VARCHAR(100) NOT NULL
);

CREATE TABLE Productos (
    id_producto   INT PRIMARY KEY,
    id_familia    INT NOT NULL,
    id_duracion   INT NOT NULL,
    FOREIGN KEY (id_familia) REFERENCES Codigos(codigo),
    FOREIGN KEY (id_duracion) REFERENCES Codigos(codigo)
);

CREATE TABLE Articulos (
    id_articulo   INT PRIMARY KEY,
    id_producto   INT NOT NULL,
    id_tamano     INT NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto),
    FOREIGN KEY (id_tamano) REFERENCES Codigos(codigo)
);

CREATE TABLE Clientes (
    id_cliente    INT PRIMARY KEY,
    nombre        VARCHAR(150) NOT NULL,
    direccion     VARCHAR(150) NOT NULL,
    telefono      VARCHAR(20),
    ciudad        INT NOT NULL,
    departamento  INT NOT NULL,
    provincia     INT NOT NULL,
    rubro         INT NOT NULL,
    categoria     VARCHAR(50),
    fecha_alta    DATE,
    FOREIGN KEY (ciudad) REFERENCES Ciudades(id_ciudad),
    FOREIGN KEY (departamento) REFERENCES Departamentos(id_depto),
    FOREIGN KEY (provincia) REFERENCES Provincia(id_provincia),
    FOREIGN KEY (rubro) REFERENCES Rubros(id_rubro)
);

CREATE TABLE Vendedores (
    id_vendedor   INT PRIMARY KEY,
    nombre        VARCHAR(150) NOT NULL,
    direccion     VARCHAR(200),
    telefono      VARCHAR(20),
    especialidad  VARCHAR(100)
);

CREATE TABLE Facturas (
    factura      INT PRIMARY KEY,
    fecha        DATE NOT NULL,
    cliente      INT NOT NULL,
    vendedor     INT NOT NULL,
    FOREIGN KEY (cliente) REFERENCES Clientes(id_cliente),
    FOREIGN KEY (vendedor) REFERENCES Vendedores(id_vendedor)
);

CREATE TABLE Promocion (
    id_promocion       INT PRIMARY KEY,
    id_articulo       INT NOT NULL,
    fecha_inicio      DATE,
    fecha_fin         DATE,
    precio_promocion  DECIMAL(18,2),
    FOREIGN KEY (id_articulo) REFERENCES Articulos(id_articulo)
);

CREATE TABLE RegistrosFacturas (
    factura        INT NOT NULL,
    articulo       INT NOT NULL,
    importe        DECIMAL(18,2) NOT NULL,
    unidades       INT NOT NULL,
    id_promocion    INT,
    PRIMARY KEY (factura, articulo),
    FOREIGN KEY (factura) REFERENCES Facturas(factura),
    FOREIGN KEY (articulo) REFERENCES Articulos(id_articulo),
    FOREIGN KEY (id_promocion) REFERENCES Promocion(id_promocion)
);

COMMIT;