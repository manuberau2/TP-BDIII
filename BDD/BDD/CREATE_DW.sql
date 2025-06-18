-- DIMENSIONES

CREATE TABLE DIM_distribucion_geografica (
    distribucion_geografica_key INT IDENTITY(1,1) PRIMARY KEY,
    zona         VARCHAR(50),
    provincia    VARCHAR(100),
    departamento VARCHAR(100),
    ciudad       VARCHAR(100)
);

CREATE TABLE DIM_producto (
    producto_key   INT PRIMARY KEY,
    nombre         VARCHAR(150),
    categoria      VARCHAR(100),
    duracion       VARCHAR(50)
);

CREATE TABLE DIM_tiempo (
    tiempo_key   INT IDENTITY(1,1) PRIMARY KEY,
    fecha        DATE,
    mes          INT,
    anio         INT,
    mes_nombre   VARCHAR(20),
    dia          INT,
    dia_nombre   VARCHAR(20)
);

CREATE TABLE DIM_rubro (
    rubro_key   INT IDENTITY(1,1) PRIMARY KEY,
    sector      VARCHAR(100)
);

CREATE TABLE DIM_vendedor (
    vendedor_key INT IDENTITY(1,1) PRIMARY KEY,
    nombre       VARCHAR(150)
);

CREATE TABLE DIM_antiguedad (
    antiguedad_key INT IDENTITY(1,1) PRIMARY KEY,
    rango_anios    VARCHAR(50)
);

CREATE TABLE DIM_capacitacion (
    capacitacion_key INT IDENTITY(1,1) PRIMARY KEY,
    franja_horaria   VARCHAR(50)
);

CREATE TABLE DIM_sueldo (
    sueldo_key    INT IDENTITY(1,1) PRIMARY KEY,
    rango_sueldo  VARCHAR(50)
);

-- TABLAS DE HECHOS

CREATE TABLE FACT_ventas (
    tiempo_key                   INT NOT NULL,
    producto_key                 INT NOT NULL,
    distribucion_geografica_key  INT NOT NULL,
    rubro_key                    INT NOT NULL,
    unidades_vendidas            INT,
    monto_total                  DECIMAL(18,2),
    descuentos                   DECIMAL(18,2),
    PRIMARY KEY (tiempo_key, producto_key, distribucion_geografica_key, rubro_key),
    FOREIGN KEY (tiempo_key) REFERENCES dim_tiempo(tiempo_key),
    FOREIGN KEY (producto_key) REFERENCES dim_producto(producto_key),
    FOREIGN KEY (distribucion_geografica_key) REFERENCES dim_distribucion_geografica(distribucion_geografica_key),
    FOREIGN KEY (rubro_key) REFERENCES dim_rubro(rubro_key)
);

CREATE TABLE FACT_desempeno_vendedores (
    tiempo_key                   INT NOT NULL,
    producto_key                 INT NOT NULL,
    capacitacion_key             INT NOT NULL,
    distribucion_geografica_key  INT NOT NULL,
    antiguedad_key               INT NOT NULL,
    sueldo_key                   INT NOT NULL,
    vendedor_key                 INT NOT NULL,
    cantidad_ventas_vendedor     INT,
    monto_total                  DECIMAL(18,2),
    PRIMARY KEY (
        tiempo_key, producto_key, capacitacion_key,
        distribucion_geografica_key, antiguedad_key,
        sueldo_key, vendedor_key
    ),
    FOREIGN KEY (tiempo_key) REFERENCES dim_tiempo(tiempo_key),
    FOREIGN KEY (producto_key) REFERENCES dim_producto(producto_key),
    FOREIGN KEY (capacitacion_key) REFERENCES dim_capacitacion(capacitacion_key),
    FOREIGN KEY (distribucion_geografica_key) REFERENCES dim_distribucion_geografica(distribucion_geografica_key),
    FOREIGN KEY (antiguedad_key) REFERENCES dim_antiguedad(antiguedad_key),
    FOREIGN KEY (sueldo_key) REFERENCES dim_sueldo(sueldo_key),
    FOREIGN KEY (vendedor_key) REFERENCES dim_vendedor(vendedor_key)
);

    CREATE TABLE FACT_almacen (
    tiempo_key       INT NOT NULL,
    producto_key     INT NOT NULL,
    cant_producto    INT,
    capital_almacen  DECIMAL(18,2),
    PRIMARY KEY (tiempo_key, producto_key),
    FOREIGN KEY (tiempo_key) REFERENCES dim_tiempo(tiempo_key),
    FOREIGN KEY (producto_key) REFERENCES dim_producto(producto_key)
);