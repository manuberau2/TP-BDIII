-- Script para eliminar todas las tablas del Data Warehouse
-- Orden: Primero tablas de hechos (FACT), luego dimensiones (DIM)

-- ELIMINAR TABLAS DE HECHOS (tienen foreign keys hacia las dimensiones)
DROP TABLE IF EXISTS FACT_almacen;
DROP TABLE IF EXISTS FACT_desempeno_vendedores;
DROP TABLE IF EXISTS FACT_ventas;

-- ELIMINAR TABLAS DE DIMENSIONES (en cualquier orden ya que no tienen dependencias entre ellas)
DROP TABLE IF EXISTS DIM_sueldo;
DROP TABLE IF EXISTS DIM_capacitacion;
DROP TABLE IF EXISTS DIM_antiguedad;
DROP TABLE IF EXISTS DIM_vendedor;
DROP TABLE IF EXISTS DIM_rubro;
DROP TABLE IF EXISTS DIM_tiempo;
DROP TABLE IF EXISTS DIM_producto;
DROP TABLE IF EXISTS DIM_distribucion_geografica;
