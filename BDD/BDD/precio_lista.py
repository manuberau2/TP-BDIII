import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Definición rango fechas y productos
fecha_inicio = datetime(2020, 1, 1)
fecha_fin = datetime(2025, 6, 13)
id_productos = range(1, 501)

# Generar lista de fechas trimestrales
fechas_vigencia = []
current_date = fecha_inicio
while current_date <= fecha_fin:
    fechas_vigencia.append(current_date)
    # Suma 3 meses: aproximado a 90 días
    current_date += timedelta(days=90)

data = []

# Generar precios para cada producto y fecha de vigencia trimestral
np.random.seed(42)  # Semilla para reproducibilidad

for producto in id_productos:
    for fecha in fechas_vigencia:
        precio = round(np.random.uniform(10, 100), 2)
        data.append([producto, fecha.strftime('%Y-%m-%d'), precio])

# Crear DataFrame
df = pd.DataFrame(data, columns=['id_producto', 'fecha_inicio', 'precio_lista'])

# Guardar a Excel
df.to_excel('precios_lista.xlsx', index=False)
print("Archivo 'precios_lista.xlsx' generado correctamente.")