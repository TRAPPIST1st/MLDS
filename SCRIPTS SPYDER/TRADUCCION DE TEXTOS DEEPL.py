# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 01:42:51 2025

@author: TRAPPIST
"""
import pandas as pd
from deep_translator import GoogleTranslator

# Ruta del archivo CSV
file_path = 'Español3.csv'
# Supongamos que tienes un archivo CSV

# Leer el archivo CSV
df = pd.read_csv(file_path, encoding='utf-8')

#Crear Dataframe JSON
df = pd.read_json('C:\\Users\\TRAPPIST\\Desktop\\TRADUCCIONES JSON\\english.json', encoding='utf-8', orient='index')

# Verificar el número de registros (filas)
print("Número de registros:", df.shape[0])


df['ORIGINAL'] = df['ORIGINAL'].fillna('none')
df['TRADUCCION'] = df['TRADUCCION'].fillna('Ninguno')


# Función para traducir con deep-translator
def translate_text(text):
    if not isinstance(text, str) or not text.strip():
        return text
    try:
        return GoogleTranslator(source='en', target='es').translate(text)
    except Exception as e:
        print(f"Error al traducir: {text}. Error: {e}")
        return text

# Traducir la columna 'ORIGINAL' y guardar el resultado en 'TRADUCCION'
df['TRADUCCION'] = df['ORIGINAL'].apply(translate_text)

# Guardar el resultado en un nuevo archivo CSV
output_path = 'archivo_traducido.csv'
df.to_csv(output_path, index=False)

print(f"Traducciones completadas. Archivo guardado en: {output_path}")

#VERIFICAR DUPLICADOS
duplicados = df[df.duplicated()]

if not duplicados.empty:
    print("Se encontraron registros duplicados:")
    print(duplicados)
else:
    print("No se encontraron registros duplicados.")
    
#TRADUCCION JSON

import pandas as pd
from deep_translator import GoogleTranslator

# Read the JSON data
df = pd.read_json('C:\\Users\\TRAPPIST\\Desktop\\TRADUCCIONES JSON\\english.json', encoding='utf-8', orient='index')
df.columns = ['English','Español']

# Fill in any missing values
df['índice'] = df['índice'].fillna('none')
df['English'] = df['English'].fillna('0')

# Function to translate using Google Translator
def translate_text(text):
    if not isinstance(text, str) or not text.strip():
        return text
    try:
        return GoogleTranslator(source='en', target='es').translate(text)
    except Exception as e:
        print(f"Error al traducir: {text}. Error: {e}")
        return text

# Translate the 'English' column and save the result in the 'Español' column
df['Español'] = df['English'].apply(translate_text)

# Save the result to a new CSV file
output_path = 'archivo_traducido.csv'
df.to_csv(output_path, index=False)

print(f"Traducciones completadas. Archivo guardado en: {output_path}")