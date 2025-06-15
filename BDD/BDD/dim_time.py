import pandas as pd
import datetime

# Fechas de inicio y fin
fecha_inicio = datetime.date(2020, 1, 1)
fecha_final = datetime.date(2025, 6, 13)

dias_semana = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']
meses = ['ENERO', 'FEBRERO', 'MARZO', 'ABRIL', 'MAYO', 'JUNIO', 
         'JULIO', 'AGOSTO', 'SEPTIEMBRE', 'OCTUBRE', 'NOVIEMBRE', 'DICIEMBRE']

fechas = []
curr_date = fecha_inicio
while curr_date <= fecha_final:
    time_key = int(curr_date.strftime('%Y%m%d'))
    fecha_str = curr_date.strftime('%Y/%m/%d')
    anio = curr_date.year
    mes = curr_date.month
    dia = curr_date.day
    dia_nombre = dias_semana[curr_date.weekday()]
    mes_nombre = meses[mes-1]
    fechas.append([time_key, fecha_str, anio, mes, dia, dia_nombre, mes_nombre])
    curr_date += datetime.timedelta(days=1)

df = pd.DataFrame(fechas, columns=["TIME_KEY", "FECHA", "ANIO", "MES", "DIA", "DIA_NOMBRE", "MES_NOMBRE"])

# Escribir a Excel
df.to_excel("dim_tiempo.xlsx", index=False)
print("Archivo dim_tiempo.xlsx creado exitosamente.")