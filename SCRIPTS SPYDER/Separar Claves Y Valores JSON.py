# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 00:58:26 2025

@author: TRAPPIST
"""

import pandas as pd

# Ruta del archivo JSON
ruta_json = r'C:\Users\TRAPPIST\Desktop\TRADUCCIONES JSON\Español3.json'

# Leer el archivo JSON
data = pd.read_json(ruta_json, orient='index')

# Separar las claves y valores
claves = data.index.to_frame(index=False)  # Extraer las claves
valores = data.reset_index(drop=True)      # Extraer los valores

# Guardar las claves en un archivo CSV
claves.to_csv('claves.csv', header=False, index=False)

# Guardar los valores en un archivo CSV
valores.to_csv('valores.csv', header=False, index=False)

print("Las columnas se han separado correctamente.")

#