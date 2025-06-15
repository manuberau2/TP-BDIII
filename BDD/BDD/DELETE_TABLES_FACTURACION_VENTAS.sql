USE FacturacionVentas;
GO

-- Eliminar tablas en orden correcto (respetando foreign keys)
DROP TABLE IF EXISTS RegistrosFacturas;
DROP TABLE IF EXISTS Promocion;
DROP TABLE IF EXISTS Facturas;
DROP TABLE IF EXISTS Clientes;
DROP TABLE IF EXISTS Vendedores;
DROP TABLE IF EXISTS Articulos;
DROP TABLE IF EXISTS Productos;
DROP TABLE IF EXISTS Codigos;
DROP TABLE IF EXISTS Rubros;
DROP TABLE IF EXISTS Ciudades;
DROP TABLE IF EXISTS Departamentos;
DROP TABLE IF EXISTS Provincia;
DROP TABLE IF EXISTS Zona;