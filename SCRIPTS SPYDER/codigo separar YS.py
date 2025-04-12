# -*- coding: utf-8 -*-
"""
Created on Tue Sep  3 21:28:04 2024

@author: TRAPPIST
"""

import pandas as pd
df = pd.read_csv('nombres_unicos.csv')


# Función para filtrar palabras con "ÿ"
def contiene_letra_ÿ(nombre):
    # Separar el nombre en palabras
    palabras = nombre.split()
    # Filtrar palabras que contienen "ÿ"
    palabras_con_ÿ = [palabra for palabra in palabras if 'ÿ' in palabra]
    # Unir las palabras filtradas nuevamente en una cadena
    return ' '.join(palabras_con_ÿ)

# Aplicar la función al DataFrame y crear un nuevo DataFrame con las palabras que contienen "ÿ"
df_con_y_dieresis = df.copy()
df_con_y_dieresis['Nombres'] = df['Nombres'].apply(contiene_letra_ÿ)

# Filtrar filas donde la columna 'nombre' no esté vacía (es decir, que realmente contenga "ÿ")
df_con_y_dieresis = df_con_y_dieresis[df_con_y_dieresis['Nombres'] != '']

# Mostrar el DataFrame resultante
print(df_con_y_dieresis)
df_con_y_dieresis.to_csv('DICCIONARIO CARACTER.csv', index=False)