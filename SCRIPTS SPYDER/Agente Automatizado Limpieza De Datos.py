# -*- coding: utf-8 -*-
"""
Created on Fri Mar 21 10:23:11 2025

@author: Valeria cardona
"""
#LIMPIA BASE DE DATOS
import os
import time
import pandas as pd
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Directorios de entrada y salida
INPUT_DIR = r'C:\Users\TRAPPIST\Desktop\Limpieza'
OUTPUT_DIR = r'C:\Users\TRAPPIST\Desktop\Limpieza\cleaned_data'

# Asegurarse de que los directorios existen
os.makedirs(INPUT_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

def clean_csv(file_path, output_path):
    # Leer el CSV
    df = pd.read_csv(file_path)
    
    # 1. Eliminar filas duplicadas
    df = df.drop_duplicates()
    
    # 2. Rellenar valores faltantes:
    # Para columnas numéricas, se usa la mediana; para texto, la moda.
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col].fillna(df[col].median(), inplace=True)
        else:
            df[col].fillna(df[col].mode()[0], inplace=True)
    
    # 3. Normalizar texto: eliminar espacios en blanco y convertir a minúsculas en columnas de tipo objeto
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].str.strip().str.lower()
    
    # Guardar el CSV limpio en la carpeta de salida
    df.to_csv(output_path, index=False)
    print(f"Archivo procesado y guardado en: {output_path}")

class CSVHandler(FileSystemEventHandler):
    def on_created(self, event):
        # Procesa únicamente archivos CSV
        if not event.is_directory and event.src_path.endswith('.csv'):
            print(f"Nuevo archivo detectado: {event.src_path}")
            # Espera un momento para asegurarse de que el archivo se haya terminado de escribir
            time.sleep(1)
            file_name = os.path.basename(event.src_path)
            output_file = os.path.join(OUTPUT_DIR, file_name)
            clean_csv(event.src_path, output_file)

if __name__ == "__main__":
    event_handler = CSVHandler()
    observer = Observer()
    observer.schedule(event_handler, INPUT_DIR, recursive=False)
    observer.start()
    print(f"Monitorizando la carpeta '{INPUT_DIR}' en busca de nuevos archivos CSV...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
