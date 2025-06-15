USE RecursosHumanos;
GO

-- Primero eliminar tablas que tienen claves foráneas (hijas)
DROP TABLE IF EXISTS EmpleadoAusencia;
DROP TABLE IF EXISTS CapacitacionXEmpleado;
DROP TABLE IF EXISTS CategoriaEmpleado;
DROP TABLE IF EXISTS TelefonoEmpleado;
DROP TABLE IF EXISTS BasicoCategoria;

-- Luego eliminar tablas que son referenciadas (padres)
DROP TABLE IF EXISTS MotivoAusencia;
DROP TABLE IF EXISTS Capacitacion;
DROP TABLE IF EXISTS Categoria;
DROP TABLE IF EXISTS Empleado;
DROP TABLE IF EXISTS Locales;
