# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 10:10:15 2025

@author: Valeria cardona
"""
#CREA BASE DE DATOS
import csv
import random
from faker import Faker

fake = Faker()
rows = []

# Encabezados del CSV
rows.append(["Name", "Age", "Email", "Join_Date"])

# Generar 2000 filas de datos con errores
for _ in range(5000):
    name = fake.name()
    age = random.randint(18, 80)
    email = fake.email()
    join_date = fake.date_between(start_date="-5y", end_date="today").strftime("%Y-%m-%d")
    
    # Introducir errores: posibilidad de valores faltantes en cada campo (5% de probabilidad)
    if random.random() < 0.05:
        name = ""
    if random.random() < 0.05:
        age = ""
    if random.random() < 0.05:
        email = ""
    if random.random() < 0.05:
        join_date = ""
    
    # Errores en el formato de fecha: 10% de probabilidad de cambiar el formato o agregar espacios
    if join_date and random.random() < 0.1:
        if random.random() < 0.5:
            join_date = join_date.replace("-", "/")
        else:
            join_date = " " + join_date.strip() + " "
    
    # Preparar la fila de datos
    row = [name, age, email, join_date]
    rows.append(row)
    
    # Duplicar la fila con una probabilidad del 5%
    if random.random() < 0.05:
        rows.append(row)

# Escribir los datos en un archivo CSV
with open("datos_erroneos.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print("Archivo 'datos_erroneos.csv' generado con éxito.")
