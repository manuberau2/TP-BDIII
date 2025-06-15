import pyodbc
import random
from faker import Faker
from datetime import datetime, timedelta

# Configuración de conexión
server = 'database-distribuidora.database.windows.net'
database = 'RecursosHumanos'
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
faker = Faker('es_AR')

# Cantidad de registros
N_LOCALES = 25
N_EMPLEADOS = 350
N_CAPACITACIONES = 50
N_MOTIVOS_AUSENCIA = 10
N_CATEGORIAS = 8

# Helper para insertar en bloque
def insert_many(query, data):
    cursor.fast_executemany = True
    cursor.executemany(query, data)

# Datos de ejemplo para Argentina
provincias_ciudades = {
    "Buenos Aires": ["La Plata", "Mar del Plata", "Bahía Blanca", "Quilmes", "Morón"],
    "Córdoba": ["Córdoba", "Villa María", "Río Cuarto", "Carlos Paz"],
    "Santa Fe": ["Santa Fe", "Rosario", "Rafaela", "Venado Tuerto"],
    "Mendoza": ["Mendoza", "San Rafael", "Godoy Cruz", "Maipú"],
    "Tucumán": ["San Miguel de Tucumán", "Yerba Buena", "Tafí Viejo"],
    "Entre Ríos": ["Paraná", "Concordia", "Gualeguaychú"],
    "Salta": ["Salta", "Cafayate", "Orán"],
    "Chaco": ["Resistencia", "Barranqueras", "Fontana"]
}

print("Cargando Locales...")
locales = []
for i in range(N_LOCALES):
    provincia = random.choice(list(provincias_ciudades.keys()))
    ciudad = random.choice(provincias_ciudades[provincia])
    locales.append((
        i+1,
        f"Sucursal {ciudad}",
        faker.street_address(),
        ciudad,
        provincia
    ))
insert_many("INSERT INTO Locales (id_local, nombre_local, direccion, ciudad, provincia) VALUES (?, ?, ?, ?, ?)", locales)

print("Cargando Categorías...")
categorias = [
    "Director",
    "Gerente Senior",
    "Gerente",
    "Supervisor Senior",
    "Supervisor",
    "Vendedor Senior",
    "Vendedor Junior",
    "Administrativo"
]
cat_data = [(i+1, cat) for i, cat in enumerate(categorias)]
insert_many("INSERT INTO Categoria (id_categoria_salarial, descripcion) VALUES (?, ?)", cat_data)

print("Cargando Básicos por Categoría...")
fecha_actual = datetime.now().date()  # Convertir a date para eliminar la parte de tiempo
fecha_inicio = (fecha_actual - timedelta(days=730)).strftime('%Y-%m-%d')  # 2 años atrás
fecha_fin = (fecha_actual - timedelta(days=365)).strftime('%Y-%m-%d')  # 1 año atrás
fecha_actual = fecha_actual.strftime('%Y-%m-%d')

# Definir salarios base por categoría (valores en pesos argentinos)
salarios_base = {
    "Director": 500000,
    "Gerente Senior": 400000,
    "Gerente": 300000,
    "Supervisor Senior": 250000,
    "Supervisor": 200000,
    "Vendedor Senior": 180000,
    "Vendedor Junior": 150000,
    "Administrativo": 120000
}

basicos_categoria = []
# Generar dos períodos de básicos con aumento
for periodo, fecha in [(1, fecha_inicio), (2, fecha_fin)]:
    for i, categoria in enumerate(categorias):
        salario_base = salarios_base[categoria]
        if periodo == 2:
            salario_base = round(salario_base * 1.45, 2)  # 45% de aumento en el segundo período
        
        basicos_categoria.append((
            i+1,
            fecha,
            fecha_fin if periodo == 1 else None,
            salario_base
        ))

insert_many("INSERT INTO BasicoCategoria (id_categoria_salarial, fecha_inicio_vigencia, fecha_fin_vigencia, salario_basico) VALUES (?, ?, ?, ?)", basicos_categoria)

print("Cargando Empleados...")
empleados = []
categoria_empleados = []

# Asegurar que haya suficientes vendedores (80 como en facturación)
n_vendedores = 80
n_otros_empleados = N_EMPLEADOS - n_vendedores

# Fecha límite para cambios (30 días antes de hoy)
fecha_limite_cambios = (datetime.now() - timedelta(days=30)).date()

def generar_fecha_cambio(fecha_ingreso_dt):
    """
    Genera una fecha de cambio válida entre la fecha de ingreso y la fecha límite
    """
    fecha_minima = fecha_ingreso_dt + timedelta(days=180)  # 6 meses después del ingreso
    
    if fecha_minima >= fecha_limite_cambios:
        return None
        
    try:
        return faker.date_between(
            start_date=fecha_minima,
            end_date=fecha_limite_cambios
        )
    except:
        return None

# Primero generar vendedores
for i in range(n_vendedores):
    # Convertir fecha_ingreso a objeto date para comparaciones
    fecha_ingreso_dt = faker.date_between(start_date='-5y', end_date='-6m')
    fecha_ingreso = fecha_ingreso_dt.strftime('%Y-%m-%d')
    
    # Probabilidad de cambio de categoría (30% de los vendedores)
    if random.random() < 0.3:
        fecha_cambio_dt = generar_fecha_cambio(fecha_ingreso_dt)
        
        if fecha_cambio_dt:
            fecha_cambio = fecha_cambio_dt.strftime('%Y-%m-%d')
            
            # Período inicial como Junior
            categoria_empleados.append((
                7,  # Vendedor Junior
                i+1,  # legajo
                fecha_ingreso,
                fecha_cambio  # fecha fin como Junior
            ))
            
            # Promoción a Senior
            categoria = 6  # Vendedor Senior
            categoria_empleados.append((
                categoria,
                i+1,  # legajo
                fecha_cambio,  # fecha inicio como Senior
                None
            ))
        else:
            # Si no se pudo generar fecha de cambio, se queda en categoría inicial
            categoria = random.choice([6, 7])  # Senior o Junior
            categoria_empleados.append((
                categoria,
                i+1,  # legajo
                fecha_ingreso,
                None
            ))
    else:
        # Sin cambio de categoría
        categoria = random.choice([6, 7])  # Senior o Junior
        categoria_empleados.append((
            categoria,
            i+1,  # legajo
            fecha_ingreso,
            None
        ))
    
    # Obtener el sueldo base de la última categoría
    sueldo_base = next(b[3] for b in basicos_categoria if b[0] == categoria and b[2] is None)
    sueldo = round(sueldo_base * random.uniform(0.9, 1.1), 2)
    
    empleados.append((
        i+1,  # legajo
        faker.first_name(),
        faker.last_name(),
        faker.street_address(),
        sueldo,
        fecha_ingreso,
        random.randint(1, N_LOCALES)  # id_local
    ))

# Luego generar otros empleados
for i in range(n_vendedores, N_EMPLEADOS):
    # Convertir fecha_ingreso a objeto date para comparaciones
    fecha_ingreso_dt = faker.date_between(start_date='-5y', end_date='-1m')
    fecha_ingreso = fecha_ingreso_dt.strftime('%Y-%m-%d')
    
    # Determinar categoría inicial
    if i < n_vendedores + 2:
        categoria_inicial = 2  # Empezó como Gerente Senior
        categoria_final = 1    # Promovido a Director
    elif i < n_vendedores + 6:
        categoria_inicial = 3  # Empezó como Gerente
        categoria_final = 2    # Promovido a Gerente Senior
    elif i < n_vendedores + 12:
        categoria_inicial = 4  # Empezó como Supervisor Senior
        categoria_final = 3    # Promovido a Gerente
    else:
        # Para el resto, algunos tienen promociones dentro de niveles más bajos
        if random.random() < 0.2:  # 20% de probabilidad de promoción
            categoria_inicial = 5  # Supervisor
            categoria_final = 4    # Supervisor Senior
        else:
            categoria_inicial = random.choice([4, 5, 8])
            categoria_final = None
    
    # Si tiene categoría final, intentar generar fecha de cambio
    if categoria_final is not None:
        fecha_cambio_dt = generar_fecha_cambio(fecha_ingreso_dt)
        
        if fecha_cambio_dt:
            fecha_cambio = fecha_cambio_dt.strftime('%Y-%m-%d')
            
            # Período inicial
            categoria_empleados.append((
                categoria_inicial,
                i+1,
                fecha_ingreso,
                fecha_cambio
            ))
            
            # Período después de la promoción
            categoria_empleados.append((
                categoria_final,
                i+1,
                fecha_cambio,
                None
            ))
            
            # Usar el sueldo de la categoría final
            categoria = categoria_final
        else:
            # Si no se pudo generar fecha de cambio, se queda en categoría inicial
            categoria_empleados.append((
                categoria_inicial,
                i+1,
                fecha_ingreso,
                None
            ))
            categoria = categoria_inicial
    else:
        # Sin cambio de categoría
        categoria_empleados.append((
            categoria_inicial,
            i+1,
            fecha_ingreso,
            None
        ))
        categoria = categoria_inicial
    
    # Obtener el sueldo base de la última categoría
    sueldo_base = next(b[3] for b in basicos_categoria if b[0] == categoria and b[2] is None)
    sueldo = round(sueldo_base * random.uniform(0.9, 1.1), 2)
    
    empleados.append((
        i+1,
        faker.first_name(),
        faker.last_name(),
        faker.street_address(),
        sueldo,
        fecha_ingreso,
        random.randint(1, N_LOCALES)
    ))

# Primero insertar los empleados
print("Insertando registros de Empleados...")
insert_many("INSERT INTO Empleado (legajo, nombre, apellido, direccion, sueldo, fecha_ingreso, id_local) VALUES (?, ?, ?, ?, ?, ?, ?)", empleados)

# Luego insertar las categorías
print("Insertando registros de Categorías de Empleados...")
insert_many("INSERT INTO CategoriaEmpleado (id_categoria_salarial, legajo, fecha_inicio, fecha_fin) VALUES (?, ?, ?, ?)", categoria_empleados)

print("Cargando Teléfonos de Empleados...")
telefonos = []
for emp in empleados:
    legajo = emp[0]
    # Generar 1 o 2 teléfonos por empleado
    n_telefonos = random.randint(1, 2)
    for _ in range(n_telefonos):
        telefonos.append((
            legajo,
            f"+54 {random.choice(['11', '351', '341', '261'])} {random.randint(1000,9999)}-{random.randint(1000,9999)}"
        ))
insert_many("INSERT INTO TelefonoEmpleado (legajo, telefono_empleado) VALUES (?, ?)", telefonos)

print("Cargando Capacitaciones...")
tipos_capacitacion = [
    "Técnicas de Venta",
    "Atención al Cliente",
    "Liderazgo",
    "Gestión de Equipos",
    "Productos Nuevos",
    "Manejo de Conflictos",
    "Excel Avanzado",
    "Gestión de Inventario",
    "Negociación",
    "Marketing Digital"
]

capacitaciones = []
for i in range(N_CAPACITACIONES):
    tipo = random.choice(tipos_capacitacion)
    nivel = random.choice(["Básico", "Intermedio", "Avanzado"])
    duracion = random.randint(4, 40)
    fecha = faker.date_between(start_date='-2y', end_date='+6m').strftime('%Y-%m-%d')
    
    capacitaciones.append((
        i+1,
        f"{tipo} - Nivel {nivel}",
        duracion,
        fecha
    ))
insert_many("INSERT INTO Capacitacion (id_capacitacion, descripcion, duracion_horas, fecha_inicio) VALUES (?, ?, ?, ?)", capacitaciones)

print("Cargando Capacitaciones por Empleado...")
capacitaciones_empleado = []
fecha_actual = datetime.now().date()

for emp in empleados:
    legajo = emp[0]
    # Cada empleado tiene entre 1 y 4 capacitaciones
    n_capacitaciones = random.randint(1, 4)
    caps_asignadas = random.sample(range(1, N_CAPACITACIONES + 1), n_capacitaciones)
    
    for cap in caps_asignadas:
        # Solo asignar resultado si la capacitación ya pasó
        fecha_cap = datetime.strptime(next(c[3] for c in capacitaciones if c[0] == cap), '%Y-%m-%d').date()
        if fecha_cap <= fecha_actual:
            resultado = random.choice(["Aprobado", "Aprobado", "Aprobado", "En Curso", "No Aprobado"])
        else:
            resultado = "Pendiente"
        
        capacitaciones_empleado.append((
            cap,
            legajo,
            resultado
        ))
insert_many("INSERT INTO CapacitacionXEmpleado (id_capacitacion, legajo, resultado) VALUES (?, ?, ?)", capacitaciones_empleado)

print("Cargando Motivos de Ausencia...")
motivos = [
    "Enfermedad",
    "Trámites personales",
    "Licencia por estudio",
    "Licencia por maternidad/paternidad",
    "Vacaciones",
    "Licencia sin goce de sueldo",
    "Capacitación externa",
    "Duelo familiar",
    "Mudanza",
    "Otros"
]
motivos_ausencia = [(i+1, motivo) for i, motivo in enumerate(motivos)]
insert_many("INSERT INTO MotivoAusencia (cod_motivo, descripcion) VALUES (?, ?)", motivos_ausencia)

print("Cargando Ausencias de Empleados...")
ausencias = []
for emp in empleados:
    legajo = emp[0]
    # Generar entre 0 y 10 ausencias por empleado
    n_ausencias = random.randint(0, 10)
    fechas_usadas = set()
    
    for _ in range(n_ausencias):
        fecha = faker.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d')
        # Evitar duplicados de fecha para el mismo empleado
        while fecha in fechas_usadas:
            fecha = faker.date_between(start_date='-1y', end_date='today').strftime('%Y-%m-%d')
        
        fechas_usadas.add(fecha)
        motivo = random.randint(1, len(motivos))
        
        ausencias.append((
            legajo,
            fecha,
            motivo
        ))

insert_many("INSERT INTO EmpleadoAusencia (legajo, fecha_ausencia, cod_motivo) VALUES (?, ?, ?)", ausencias)

print("¡Carga de datos de RRHH completada!")
conn.commit()
cursor.close()
conn.close()
