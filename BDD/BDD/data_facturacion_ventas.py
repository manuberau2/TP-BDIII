import pyodbc
import random
from faker import Faker
from datetime import datetime, timedelta

# Configuración de conexión
server = 'database-distribuidora.database.windows.net'
database = 'FacturacionVentas'
username = 'sqladmin@database-distribuidora'
password = 'Manu_2025'

conn_str = (
    'DRIVER={ODBC Driver 18 for SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    f'UID={username};'
    f'PWD={password};'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=60;'
)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()
faker = Faker('es_AR')  # Cambiado a español de Argentina

# Cantidad de registros
N_DEPTOS = 24  # Argentina tiene 23 provincias + CABA
N_CIUDADES = 80
N_RUBROS = 20
N_CODIGOS = 300
N_PRODUCTOS = 500
N_ARTICULOS = 1500
N_CLIENTES = 5000
N_VENDEDORES = 80
N_FACTURAS = 15000
N_REGISTROS_FACTURAS = 45000
N_PROMOCIONES = 800

# Definir rango de fechas para análisis temporal - 5 años de historia
rango_fecha_inicio = datetime.now() - timedelta(days=1825)  # 5 años atrás (365 * 5)
rango_fecha_fin = datetime.now()

# Definir factores estacionales por mes (1.0 = promedio, >1.0 = más ventas, <1.0 = menos ventas)
factores_estacionales = {
    1: 0.8,   # Enero - post fiestas, menos actividad
    2: 0.9,   # Febrero - vuelta a clases
    3: 1.1,   # Marzo - inicio otoño, reposición
    4: 1.0,   # Abril - normal
    5: 0.9,   # Mayo - otoño
    6: 0.8,   # Junio - invierno, menos actividad
    7: 0.8,   # Julio - vacaciones invierno
    8: 1.0,   # Agosto - vuelta actividad
    9: 1.2,   # Septiembre - primavera, día del niño
    10: 1.1,  # Octubre - primavera
    11: 1.3,  # Noviembre - preparación fiestas
    12: 1.4   # Diciembre - fiestas, mayor consumo
}

# Helper para insertar en bloque (más rápido)
def insert_many(query, data):
    cursor.fast_executemany = True
    cursor.executemany(query, data)

# Datos reales de Argentina
provincias_argentinas = [
    "Buenos Aires", "Ciudad Autónoma de Buenos Aires", "Catamarca", "Chaco", 
    "Chubut", "Córdoba", "Corrientes", "Entre Ríos", "Formosa", "Jujuy", 
    "La Pampa", "La Rioja", "Mendoza", "Misiones", "Neuquén", "Río Negro",
    "Salta", "San Juan", "San Luis", "Santa Cruz", "Santa Fe", 
    "Santiago del Estero", "Tierra del Fuego", "Tucumán"
]

zonas_argentinas = {
    "Norte": ["Jujuy", "Salta", "Tucumán", "Catamarca", "La Rioja", "Santiago del Estero", "Formosa", "Chaco"],
    "Centro": ["Buenos Aires", "Ciudad Autónoma de Buenos Aires", "Córdoba", "Santa Fe", "Entre Ríos", "La Pampa"],
    "Cuyo": ["Mendoza", "San Juan", "San Luis"],
    "Patagonia": ["Neuquén", "Río Negro", "Chubut", "Santa Cruz", "Tierra del Fuego"],
    "Litoral": ["Misiones", "Corrientes"]
}

# Función para obtener la zona de una provincia
def obtener_zona(provincia):
    for zona, provincias in zonas_argentinas.items():
        if provincia in provincias:
            return zona
    return "Centro"  # Default

print("Cargando Zonas...")
zonas = []
zona_id = 1
for zona_nombre in zonas_argentinas.keys():
    zonas.append((zona_id, zona_nombre))
    zona_id += 1
insert_many("INSERT INTO Zona (id_zona, nom_zona) VALUES (?, ?)", zonas)

print("Cargando Provincias...")
provincias = []
for i, provincia in enumerate(provincias_argentinas):
    zona_nombre = obtener_zona(provincia)
    zona_id = next(z[0] for z in zonas if z[1] == zona_nombre)
    provincias.append((i+1, provincia, zona_id))
insert_many("INSERT INTO Provincia (id_provincia, nom_provincia, id_zona) VALUES (?, ?, ?)", provincias)

print("Cargando Departamentos...")
# Departamentos reales por provincia (algunos ejemplos principales)
departamentos_por_provincia = {
    "Buenos Aires": ["La Plata", "General Pueyrredón", "Bahía Blanca", "Tandil", "Quilmes", "Morón", "San Nicolás", "Pergamino"],
    "Córdoba": ["Capital", "Río Cuarto", "San Justo", "Marcos Juárez", "General San Martín", "Colón"],
    "Santa Fe": ["La Capital", "Rosario", "Castellanos", "General López", "San Lorenzo", "Constitución"],
    "Mendoza": ["Capital", "San Rafael", "Godoy Cruz", "Maipú", "Tunuyán", "San Martín"],
    "Tucumán": ["Capital", "Yerba Buena", "Tafí Viejo", "Famaillá", "Monteros"],
    "Entre Ríos": ["Paraná", "Concordia", "Gualeguaychú", "Uruguay", "Colón"],
    "Salta": ["Capital", "Cafayate", "Orán", "Metán", "Tartagal"],
    "Chaco": ["San Fernando", "Comandante Fernández", "Almirante Brown", "Maipú"],
    "Misiones": ["Capital", "Oberá", "Eldorado", "Iguazú", "San Pedro"],
    "Neuquén": ["Confluencia", "Zapala", "Chos Malal", "Picún Leufú"],
    "Río Negro": ["Viedma", "Bariloche", "General Roca", "El Bolsón"],
    "Chubut": ["Rawson", "Comodoro Rivadavia", "Puerto Madryn", "Esquel"],
    "Santa Cruz": ["Río Gallegos", "Caleta Olivia", "Puerto Deseado"],
    "Tierra del Fuego": ["Ushuaia", "Río Grande", "Tolhuin"],
    "La Pampa": ["Capital", "General Pico", "Realicó"],
    "La Rioja": ["Capital", "Chilecito", "Chamical"],
    "San Juan": ["Capital", "Caucete", "Rawson", "Chimbas"],
    "San Luis": ["Capital", "Villa Mercedes", "Junín"],
    "Catamarca": ["Capital", "Andalgalá", "Belén"],
    "Jujuy": ["Capital", "Palpalá", "San Pedro"],
    "Formosa": ["Capital", "Clorinda", "Pirané"],
    "Santiago del Estero": ["Capital", "La Banda", "Añatuya"],
    "Corrientes": ["Capital", "Goya", "Mercedes"],
    "Ciudad Autónoma de Buenos Aires": ["Comuna 1", "Comuna 2", "Comuna 3", "Comuna 4", "Comuna 5"]
}

departamentos = []
depto_id = 1

for id_provincia, provincia, zona_id in provincias:
    if provincia in departamentos_por_provincia:
        for depto_nombre in departamentos_por_provincia[provincia]:
            departamentos.append((depto_id, depto_nombre, id_provincia))
            depto_id += 1

print(f"Total de departamentos cargados: {len(departamentos)}")
insert_many("INSERT INTO Departamentos (id_depto, nom_depto, id_provincia) VALUES (?, ?, ?)", departamentos)

print("Cargando Ciudades...")
ciudades = []
ciudad_id = 1

# Agregar ciudades reales asociadas a departamentos
# Crear un mapeo de departamentos a ciudades más realista
ciudades_por_departamento = {
    # Buenos Aires
    "La Plata": ["La Plata", "Ensenada", "Berisso"],
    "General Pueyrredón": ["Mar del Plata", "Batán"],
    "Bahía Blanca": ["Bahía Blanca", "Punta Alta"],
    "Tandil": ["Tandil", "Rauch"],
    "Quilmes": ["Quilmes", "Bernal"],
    "Morón": ["Morón", "Castelar", "Haedo"],
    "San Nicolás": ["San Nicolás", "Ramallo"],
    "Pergamino": ["Pergamino", "Arrecifes"],
    
    # Córdoba
    "Capital": ["Córdoba"],
    "Río Cuarto": ["Río Cuarto", "Las Higueras"],
    "San Justo": ["San Francisco", "Morteros"],
    "Marcos Juárez": ["Marcos Juárez", "Leones"],
    "General San Martín": ["Villa María", "Villa Nueva"],
    "Colón": ["Jesús María", "Colonia Caroya"],
    
    # Santa Fe
    "La Capital": ["Santa Fe", "Santo Tomé"],
    "Rosario": ["Rosario", "Villa Gobernador Gálvez"],
    "Castellanos": ["Rafaela", "Sunchales"],
    "General López": ["Venado Tuerto", "Firmat"],
    "San Lorenzo": ["San Lorenzo", "Puerto General San Martín"],
    "Constitución": ["Villa Constitución", "Peyrano"],
    
    # Otras provincias - usar ciudades existentes
    "Confluencia": ["Neuquén Capital", "Cipolletti", "Plottier"],
    "Viedma": ["Viedma", "Carmen de Patagones"],
    "Bariloche": ["San Carlos de Bariloche", "Dina Huapi"],
    "General Roca": ["General Roca", "Allen"],
    "Rawson": ["Rawson", "Trelew"],
    "Comodoro Rivadavia": ["Comodoro Rivadavia", "Rada Tilly"],
    "Puerto Madryn": ["Puerto Madryn", "Puerto Pirámides"],
    "Río Gallegos": ["Río Gallegos", "El Calafate"],
    "Ushuaia": ["Ushuaia", "Tolhuin"],
    "Río Grande": ["Río Grande", "San Sebastián"],
    
    # Agregar más departamentos para evitar usar nombres duplicados
    "Zapala": ["Zapala", "Cutral Có"],
    "Chos Malal": ["Chos Malal", "Andacollo"],
    "Picún Leufú": ["Picún Leufú", "Piedra del Águila"],
    "El Bolsón": ["El Bolsón", "Lago Puelo"],
    "Esquel": ["Esquel", "Trevelin"],
    "Caleta Olivia": ["Caleta Olivia", "Pico Truncado"],
    "Puerto Deseado": ["Puerto Deseado", "Jaramillo"],
    "Tolhuin": ["Tolhuin", "Lago Escondido"]
}

# Agregar ciudades basadas en departamentos
ciudades_agregadas = set()  # Para evitar duplicados

for id_depto, nom_depto, id_provincia in departamentos:
    if nom_depto in ciudades_por_departamento:
        for ciudad in ciudades_por_departamento[nom_depto]:
            # Verificar si la ciudad ya fue agregada
            if ciudad not in ciudades_agregadas:
                ciudades.append((
                    ciudad_id,
                    id_depto,
                    ciudad,
                    random.randint(10000, 3000000),
                    random.choice(['urbana', 'rural', 'turística'])
                ))
                ciudades_agregadas.add(ciudad)
                ciudad_id += 1
    else:
        # Para departamentos sin mapeo específico, usar el nombre del departamento como ciudad
        # Pero solo si no existe ya una ciudad con ese nombre
        ciudad_nombre = nom_depto
        if ciudad_nombre not in ciudades_agregadas:
            ciudades.append((
                ciudad_id,
                id_depto,
                ciudad_nombre,
                random.randint(10000, 500000),
                random.choice(['urbana', 'rural', 'turística'])
            ))
            ciudades_agregadas.add(ciudad_nombre)
            ciudad_id += 1

# Actualizar N_CIUDADES al número real de ciudades generadas
N_CIUDADES = len(ciudades)
print(f"Total de ciudades reales cargadas: {N_CIUDADES}")

insert_many("INSERT INTO Ciudades (id_ciudad, id_depto, nom_ciudad, poblacion, clasificacion) VALUES (?, ?, ?, ?, ?)", ciudades)

print("Cargando Rubros...")
rubros_lista = [
    "Mayorista", "Supermercado", "Almacén", "Restaurante", 
    "Cooperativa Agraria", "Distribuidor Regional", "Mercado Central",
    "Hipermercado", "Autoservicio"
]
rubros = [(i+1, rubro) for i, rubro in enumerate(rubros_lista)]
insert_many("INSERT INTO Rubros (id_rubro, nom_rubro) VALUES (?, ?)", rubros)

print("Cargando Codigos (familia, tamaño, duración, etc)...")
tipos = ['familia', 'duracion', 'tamano']
familias_productos = [
    'Bebidas', 'Lácteos', 'Panificados', 'Productos Agrícolas', 
    'Envasados', 'Vegetales', 'Frutas', 'Congelados'
]
duraciones_productos = [
    'Ultra Perecedero', 'Perecedero Corto Plazo', 'Perecedero Mediano Plazo',
    'Larga Duración', 'No Perecedero'
]
tamanios_productos = [
    'Individual', 'Familiar', 'Mayorista',
    'Pequeño', 'Mediano', 'Grande', 'Extra Grande',
    '250ml', '500ml', '1L', '2L', '5L',
    '250g', '500g', '1kg', '5kg', '10kg', '25kg'
]

codigos = []
codigo_id = 1

# Agregar todas las familias
for familia in familias_productos:
    codigos.append((codigo_id, 'familia', familia))
    codigo_id += 1

# Agregar todas las duraciones
for duracion in duraciones_productos:
    codigos.append((codigo_id, 'duracion', duracion))
    codigo_id += 1

# Agregar todos los tamaños
for tamanio in tamanios_productos:
    codigos.append((codigo_id, 'tamano', tamanio))
    codigo_id += 1

insert_many("INSERT INTO Codigos (codigo, tipo, descripcion) VALUES (?, ?, ?)", codigos)

print("Cargando Productos...")
productos = []
# Mapeo de familia a duración típica
familia_duracion = {
    'Lácteos': ['Ultra Perecedero', 'Perecedero Corto Plazo'],
    'Panificados': ['Ultra Perecedero'],
    'Vegetales': ['Perecedero Corto Plazo'],
    'Frutas': ['Perecedero Corto Plazo'],
    'Bebidas': ['Larga Duración', 'No Perecedero'],
    'Envasados': ['Larga Duración', 'No Perecedero'],
    'Congelados': ['Perecedero Mediano Plazo'],
    'Productos Agrícolas': ['Perecedero Corto Plazo', 'Perecedero Mediano Plazo']
}

for i in range(N_PRODUCTOS):
    # Seleccionar familia
    familia = random.choice(familias_productos)
    # Seleccionar duración apropiada para esa familia
    duracion = random.choice(familia_duracion[familia])
    
    # Encontrar los IDs correspondientes en la tabla de códigos
    familia_id = next(cod[0] for cod in codigos if cod[1] == 'familia' and cod[2] == familia)
    duracion_id = next(cod[0] for cod in codigos if cod[1] == 'duracion' and cod[2] == duracion)
    
    productos.append((i+1, familia_id, duracion_id))

insert_many("INSERT INTO Productos (id_producto, id_familia, id_duracion) VALUES (?, ?, ?)", productos)

print("Cargando Articulos...")
articulos = []
for i in range(N_ARTICULOS):
    producto_id = random.randint(1, N_PRODUCTOS)
    # Obtener la familia del producto
    producto = productos[producto_id-1]
    familia_id = producto[1]
    familia = next(cod[2] for cod in codigos if cod[0] == familia_id)
    
    # Seleccionar tamaños apropiados según la familia
    if familia in ['Bebidas']:
        tamanios = ['250ml', '500ml', '1L', '2L', '5L']
    elif familia in ['Lácteos', 'Envasados']:
        tamanios = ['250g', '500g', '1kg']
    elif familia in ['Productos Agrícolas', 'Vegetales', 'Frutas']:
        tamanios = ['1kg', '5kg', '10kg', '25kg']
    else:
        tamanios = ['Individual', 'Familiar', 'Mayorista']
    
    tamanio = random.choice(tamanios)
    tamanio_id = next(cod[0] for cod in codigos if cod[1] == 'tamano' and cod[2] == tamanio)
    
    articulos.append((i+1, producto_id, tamanio_id))

insert_many("INSERT INTO Articulos (id_articulo, id_producto, id_tamano) VALUES (?, ?, ?)", articulos)

print("Cargando Clientes...")
# Distribución de clientes por rubro (porcentajes aproximados)
distribucion_rubros = {
    "Mayorista": 12,
    "Supermercado": 20,
    "Almacén": 35,  # Aumentar almacenes (más comunes)
    "Restaurante": 18,
    "Cooperativa Agraria": 3,
    "Distribuidor Regional": 4,
    "Mercado Central": 1,
    "Hipermercado": 2,
    "Autoservicio": 5
}

clientes = []
for i in range(N_CLIENTES):
    # Seleccionar rubro basado en la distribución
    rubro_nombre = random.choices(
        list(distribucion_rubros.keys()),
        weights=list(distribucion_rubros.values())
    )[0]
    rubro_id = next(r[0] for r in rubros if r[1] == rubro_nombre)
    
    # Seleccionar ciudad, departamento y provincia
    ciudad_idx = random.randint(0, len(ciudades)-1)
    ciudad_id = ciudades[ciudad_idx][0]
    depto_id = ciudades[ciudad_idx][1]
    # Obtener provincia_id del departamento
    provincia_id = next(d[2] for d in departamentos if d[0] == depto_id)
    
    # Asignar categoría basada en el rubro
    if rubro_nombre in ["Mayorista", "Hipermercado", "Distribuidor Regional"]:
        categoria = random.choice(['A', 'A', 'B'])  # Más probabilidad de ser A
    elif rubro_nombre in ["Supermercado", "Mercado Central", "Cooperativa Agraria"]:
        categoria = random.choice(['A', 'B', 'B'])  # Más probabilidad de ser B
    else:
        categoria = random.choice(['B', 'C', 'C'])  # Más probabilidad de ser C
    
    clientes.append((
        i+1,
        faker.company(),
        faker.street_address().replace('\n',' '),
        f"+54 {random.choice(['11', '351', '341', '261', '223', '381', '342'])} {random.randint(1000,9999)}-{random.randint(1000,9999)}",
        ciudad_id,
        depto_id,
        provincia_id,
        rubro_id,
        categoria,
        faker.date_between(start_date=rango_fecha_inicio, end_date=rango_fecha_fin)  # Fechas coherentes con el período de análisis
    ))

# Asegurar que algunos clientes tengan presencia en múltiples ciudades (cadenas)
num_clientes_multi_ciudad = int(N_CLIENTES * 0.08)  # 8% de clientes con múltiples ubicaciones
for _ in range(num_clientes_multi_ciudad):
    cliente_base = random.choice(clientes)
    # Solo clientes grandes tienen múltiples ubicaciones
    if cliente_base[8] in ['A', 'B']:  # categoría A o B (ajustado índice)
        num_ubicaciones = random.randint(2, 5)
        
        for _ in range(num_ubicaciones - 1):
            ciudad_idx = random.randint(0, len(ciudades)-1)
            ciudad_id = ciudades[ciudad_idx][0]
            depto_id = ciudades[ciudad_idx][1]
            # Obtener provincia_id del departamento
            provincia_id = next(d[2] for d in departamentos if d[0] == depto_id)
            
            nuevo_cliente = list(cliente_base)
            nuevo_cliente[0] = len(clientes) + 1
            nuevo_cliente[4] = ciudad_id
            nuevo_cliente[5] = depto_id
            nuevo_cliente[6] = provincia_id
            clientes.append(tuple(nuevo_cliente))

insert_many("INSERT INTO Clientes (id_cliente, nombre, direccion, telefono, ciudad, departamento, provincia, rubro, categoria, fecha_alta) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", clientes)

print("Cargando Vendedores...")
especialidades = [
    'Productos Secos y Envasados',
    'Lácteos y Congelados',
    'Panificados',
    'Productos Agrícolas y Frescos',
    'Bebidas',
    'Ventas Generales',
    'Productos Premium',
    'Distribución Mayorista'
]

# Asignar vendedores por zona para mejor cobertura
vendedores = []
for i in range(N_VENDEDORES):
    # Asignar especialidad basada en las familias de productos
    especialidad = random.choice(especialidades)
    vendedores.append((
        i+1,
        faker.name(),
        faker.street_address().replace('\n',' '),
        f"+54 {random.choice(['11', '351', '341', '261', '223', '381', '342'])} {random.randint(1000,9999)}-{random.randint(1000,9999)}",
        especialidad
    ))
insert_many("INSERT INTO Vendedores (id_vendedor, nombre, direccion, telefono, especialidad) VALUES (?, ?, ?, ?, ?)", vendedores)

print("Cargando Facturas...")

# Primero generamos las promociones para poder distribuir mejor las facturas
print("Cargando Promociones...")
promociones = []
articulos_con_promo = set()  # Para trackear qué artículos tienen promociones

for i in range(N_PROMOCIONES):
    # Seleccionar artículo que no tenga demasiadas promociones
    articulo = random.randint(1, N_ARTICULOS)
    articulos_con_promo.add(articulo)
    
    # Obtener información del artículo para promociones más realistas
    art = articulos[articulo-1]
    prod = productos[art[1]-1]
    familia_id = prod[1]
    familia = next(cod[2] for cod in codigos if cod[0] == familia_id and cod[1] == 'familia')
    
    # Determinar duración de la promoción según el tipo de producto
    if familia in ['Lácteos', 'Panificados', 'Vegetales', 'Frutas']:
        duracion_promo = random.randint(7, 15)  # Promociones cortas para productos perecederos
    else:
        duracion_promo = random.randint(15, 45)  # Promociones más largas para productos no perecederos
    
    # Distribuir las promociones con mayor concentración en meses de alta actividad
    # Generar año con probabilidad hacia años más recientes
    año_promo = random.choices(
        [2020, 2021, 2022, 2023, 2024],
        weights=[0.1, 0.15, 0.2, 0.25, 0.3]  # Más promociones en años recientes
    )[0]
    
    # Seleccionar mes con mayor probabilidad en meses de alta actividad
    mes_promo = random.choices(
        list(factores_estacionales.keys()),
        weights=[f * 1.2 if f > 1.0 else f * 0.8 for f in factores_estacionales.values()]  # Amplificar estacionalidad para promociones
    )[0]
    
    try:
        fecha_inicio_mes = datetime(año_promo, mes_promo, 1)
        if mes_promo == 12:
            fecha_fin_mes = datetime(año_promo + 1, 1, 1) - timedelta(days=1)
        else:
            fecha_fin_mes = datetime(año_promo, mes_promo + 1, 1) - timedelta(days=1)
        
        # Asegurar que no sea futuro
        if fecha_fin_mes > datetime.now():
            fecha_fin_mes = datetime.now()
        
        if fecha_inicio_mes <= fecha_fin_mes:
            fecha_inicio_promo = faker.date_between(start_date=fecha_inicio_mes, end_date=fecha_fin_mes)
        else:
            fecha_inicio_promo = faker.date_between(start_date=rango_fecha_inicio, end_date=rango_fecha_fin)
    except:
        fecha_inicio_promo = faker.date_between(start_date=rango_fecha_inicio, end_date=rango_fecha_fin)
    
    fecha_fin_promo = fecha_inicio_promo + timedelta(days=duracion_promo)
    
    # Descuento más agresivo para perecederos
    if familia in ['Lácteos', 'Panificados', 'Vegetales', 'Frutas']:
        descuento = random.uniform(0.3, 0.5)  # 30-50% descuento
    else:
        descuento = random.uniform(0.1, 0.3)  # 10-30% descuento
    
    precio_base = random.uniform(1000, 50000)
    precio_promocion = round(precio_base * (1 - descuento), 2)
    
    promociones.append((
        i+1,
        articulo,
        fecha_inicio_promo,
        fecha_fin_promo,
        precio_promocion
    ))

insert_many("INSERT INTO Promocion (id_promocion, id_articulo, fecha_inicio, fecha_fin, precio_promocion) VALUES (?, ?, ?, ?, ?)", promociones)

# Ahora generamos las facturas con patrones estacionales y de crecimiento
facturas = []

# Generar facturas con distribución estacional y crecimiento anual
facturas_por_año = {
    2020: int(N_FACTURAS * 0.15),  # 15% - año base (COVID)
    2021: int(N_FACTURAS * 0.18),  # 18% - recuperación lenta
    2022: int(N_FACTURAS * 0.20),  # 20% - recuperación
    2023: int(N_FACTURAS * 0.22),  # 22% - crecimiento
    2024: int(N_FACTURAS * 0.25)   # 25% - año actual, mayor actividad
}

factura_id = 1
for año, facturas_año in facturas_por_año.items():
    for i in range(facturas_año):
        # Seleccionar mes con probabilidad estacional
        mes = random.choices(
            list(factores_estacionales.keys()),
            weights=list(factores_estacionales.values())
        )[0]
        
        # Generar fecha dentro del mes y año específico
        try:
            fecha_inicio = datetime(año, mes, 1)
            if mes == 12:
                fecha_fin = datetime(año + 1, 1, 1) - timedelta(days=1)
            else:
                fecha_fin = datetime(año, mes + 1, 1) - timedelta(days=1)
            
            # Asegurar que la fecha no sea futura
            if fecha_fin > datetime.now():
                fecha_fin = datetime.now()
            
            if fecha_inicio <= fecha_fin:
                fecha = faker.date_between(start_date=fecha_inicio, end_date=fecha_fin)
            else:
                continue
        except:
            continue
        
        cliente = random.randint(1, len(clientes))
        
        cliente_data = clientes[cliente-1]
        rubro_id = cliente_data[7]  # Ajustado índice: provincia está en posición 6, rubro en 7
        rubro_nombre = next(r[1] for r in rubros if r[0] == rubro_id)
        
        if rubro_nombre in ["Mayorista", "Hipermercado", "Distribuidor Regional"]:
            vendedor_pool = [v[0] for v in vendedores if v[4] != 'Ventas Generales']
        else:
            vendedor_pool = [v[0] for v in vendedores]
        
        vendedor = random.choice(vendedor_pool)
        
        facturas.append((factura_id, fecha, cliente, vendedor))
        factura_id += 1

# Actualizar N_FACTURAS al número real generado
N_FACTURAS = len(facturas)
print(f"Total de facturas generadas: {N_FACTURAS}")

insert_many("INSERT INTO Facturas (factura, fecha, cliente, vendedor) VALUES (?, ?, ?, ?)", facturas)

print("Cargando RegistrosFacturas (detalles)...")
# Crear un diccionario de promociones por artículo y ordenado por fecha
promociones_por_articulo = {}
for p in promociones:
    if p[1] not in promociones_por_articulo:
        promociones_por_articulo[p[1]] = []
    promociones_por_articulo[p[1]].append(p)

# Ordenar las promociones por fecha para cada artículo
for art_promos in promociones_por_articulo.values():
    art_promos.sort(key=lambda x: x[2])  # Ordenar por fecha_inicio

registros_pks = set()
# Asegurar que algunos registros usen artículos con promociones
n_registros_con_promo = int(N_REGISTROS_FACTURAS * 0.3)  # 30% de registros con promoción
registros_con_promo = 0

while len(registros_pks) < N_REGISTROS_FACTURAS:
    factura = random.randint(1, N_FACTURAS)
    
    # Decidir si este registro debería tener promoción
    if registros_con_promo < n_registros_con_promo:
        # Seleccionar un artículo que tenga promociones
        articulo = random.choice(list(articulos_con_promo))
        registros_con_promo += 1
    else:
        articulo = random.randint(1, N_ARTICULOS)
    
    if (factura, articulo) not in registros_pks:
        registros_pks.add((factura, articulo))

registros = []
for factura, articulo in registros_pks:
    # Obtener fecha de la factura
    fecha_factura = next(f[1] for f in facturas if f[0] == factura)
    
    # Buscar promoción vigente
    promo_vigente = None
    precio_promo = None
    if articulo in promociones_por_articulo:
        for promo in promociones_por_articulo[articulo]:
            if promo[2] <= fecha_factura <= promo[3]:
                promo_vigente = promo[0]
                precio_promo = promo[4]
                break
    
    # Calcular precio normal si no hay promoción
    if precio_promo is None:
        art = articulos[articulo-1]
        prod = productos[art[1]-1]
        familia_id = prod[1]
        familia = next(cod[2] for cod in codigos if cod[0] == familia_id and cod[1] == 'familia')
        
        if familia in ['Bebidas', 'Envasados']:
            rango_precio = (500, 15000)
        elif familia in ['Lácteos', 'Panificados']:
            rango_precio = (200, 5000)
        elif familia in ['Productos Agrícolas', 'Vegetales', 'Frutas']:
            rango_precio = (1000, 30000)
        else:
            rango_precio = (500, 50000)
        
        importe = round(random.uniform(*rango_precio), 2)
    else:
        importe = precio_promo
    
    unidades = random.randint(1, 50)
    registros.append((factura, articulo, importe, unidades, promo_vigente))

insert_many("INSERT INTO RegistrosFacturas (factura, articulo, importe, unidades, id_promocion) VALUES (?, ?, ?, ?, ?)", registros)

print("¡Carga de datos ficticios completada!")
conn.commit()
cursor.close()
conn.close()