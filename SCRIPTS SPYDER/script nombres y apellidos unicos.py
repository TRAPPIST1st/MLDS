# -*- coding: utf-8 -*-
"""
Created on Mon Sep  2 19:49:38 2024

@author: TRAPPIST
"""

import pandas as pd
import numpy as np

# Supongamos que tu DataFrame original se llama 'df'
# Si no lo has cargado aún, puedes hacerlo así:
# df = pd.read_csv('tu_archivo.csv')
df = pd.read_csv('SISBEN_base.csv')

# Crear DataFrame de nombres
nombres = pd.DataFrame({
    'Nombres': pd.concat([df['NOM1'], df['NOM2']], ignore_index=True)
}) 
# Eliminar valores nulos, vacíos y espacios en blanco
nombres = nombres[nombres['Nombres'].notna() & (nombres['Nombres'].str.strip() != '')]

# Crear DataFrame de apellidos
apellidos = pd.DataFrame({
    'Apellidos': pd.concat([df['APE1'], df['APE2']], ignore_index=True)
})

# Eliminar valores nulos, vacíos y espacios en blanco
apellidos = apellidos[apellidos['Apellidos'].notna() & (apellidos['Apellidos'].str.strip() != '')]

# Eliminar duplicados
nombres = nombres.drop_duplicates().reset_index(drop=True)
apellidos = apellidos.drop_duplicates().reset_index(drop=True)

# Mostrar los primeros registros de cada DataFrame
print("DataFrame de Nombres:")
print(nombres.head())
print(f"Total de nombres únicos: {len(nombres)}")

print("\nDataFrame de Apellidos:")
print(apellidos.head())
print(f"Total de apellidos únicos: {len(apellidos)}")

# Guardar los DataFrames en archivos CSV sin índice
nombres.to_csv('nombres_unicos.csv', index=False)
apellidos.to_csv('apellidos_unicos.csv', index=False)

print("\nSe han guardado los archivos 'nombres_unicos.csv' y 'apellidos_unicos.csv'")