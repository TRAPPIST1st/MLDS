# -*- coding: utf-8 -*-
"""
Created on Sun Jan 26 11:43:09 2025

@author: TRAPPIST
"""

import pandas as pd
from deep_translator import GoogleTranslator

# Ruta del archivo CSV
file_path = 'C:\\Users\\TRAPPIST\\Desktop\\TRADUCCIONES JSON\\valores.csv'
# Supongamos que tienes un archivo CSV

# Leer el archivo CSV
df = pd.read_csv(file_path, encoding='utf-8')

# Verificar el número de registros (filas)
print("Número de registros:", df.shape[0])

# Llenar valores nulos en la columna a traducir para evitar errores
columna_a_traducir = 'Español'
df[columna_a_traducir] = df[columna_a_traducir].fillna('none')

# Función para traducir con deep-translator
def translate_text(text):
    if not isinstance(text, str) or not text.strip():
        return text
    try:
        return GoogleTranslator(source='en', target='es').translate(text)
    except Exception as e:
        print(f"Error al traducir: {text}. Error: {e}")
        return text

# Traducir la columna especificada y reemplazar los valores en la misma columna
df[columna_a_traducir] = df[columna_a_traducir].apply(translate_text)

# Guardar el resultado en un nuevo archivo CSV
output_path = 'valores_traducido.csv'
df.to_csv(output_path, index=False)

print(f"Traducciones completadas. Archivo guardado en: {output_path}")
