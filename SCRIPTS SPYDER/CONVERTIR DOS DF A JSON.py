# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 12:13:27 2025

@author: TRAPPIST
"""

import pandas as pd

# Ruta de los archivos CSV
ruta_claves = 'claves.csv'  # Archivo que contiene las claves
ruta_valores = 'valores_traducido.csv'  # Archivo que contiene los valores

# Leer las columnas desde los CSV
df_claves = pd.read_csv(ruta_claves, header=None, names=['clave'])
df_valores = pd.read_csv(ruta_valores, header=None, names=['valor'])

# Unir las columnas clave y valor
df_combinado = pd.concat([df_claves, df_valores], axis=1)

# Convertir la primera letra de cada elemento de la columna 2 a mayúscula
df_combinado['valor'] = df_combinado['valor'].str.capitalize()


# Crear el formato JSON tipo "clave":"valor",
df_combinado['json'] = '"' + df_combinado['clave'] + '":"' + df_combinado['valor'] + '",'

# Guardar el resultado en un archivo .txt o .json
with open('resultado.json', 'w', encoding='utf-8') as file:
    file.write("{\n")
    file.write("\n".join(df_combinado['json']))
    file.write("\n}")
