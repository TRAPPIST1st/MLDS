# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 12:33:06 2024

@author: TRAPPIST
"""

import pandas as pd
import re

# Cargar los datos
data = pd.read_csv('entrega_ml.csv')

# Leer los archivos de transformaciones
transformaciones_frases_df = pd.read_csv('transformaciones_frases.dic')
transformaciones_word_df = pd.read_csv('transformaciones_word.dic')

# Eliminar valores nulos y ajustar el formato de columnas
transformaciones_frases_df = transformaciones_frases_df.dropna()
transformaciones_frases_df.columns = transformaciones_frases_df.columns.str.strip()
transformaciones_frases_df['frase'] = transformaciones_frases_df['frase'].astype(str)
transformaciones_frases_df['abreviatura'] = transformaciones_frases_df['abreviatura'].astype(str)

transformaciones_word_df = transformaciones_word_df.dropna()
transformaciones_word_df.columns = transformaciones_word_df.columns.str.strip()
transformaciones_word_df['palabra'] = transformaciones_word_df['palabra'].astype(str)
transformaciones_word_df['abreviatura'] = transformaciones_word_df['abreviatura'].astype(str)

# Crear diccionarios de transformaciones
transformaciones_frases = dict(sorted(transformaciones_frases_df[['frase', 'abreviatura']].values, key=lambda x: len(x[0]), reverse=True))
transformaciones_word = dict(sorted(transformaciones_word_df[['palabra', 'abreviatura']].values, key=lambda x: len(x[0]), reverse=True))

# Función para procesar guiones en direcciones
def procesar_guiones(direccion):
    partes = direccion.split('-')
    if len(partes) > 1:
        direccion = partes[0] + '-' + ' '.join(partes[1:]).replace('-', ' ')
    return direccion

# Función de normalización de la dirección
def normalizar_direccion(direccion, transformaciones):
    direccion = direccion.upper()
    direccion = re.sub(r'[^A-Z0-9\s\-#]', '', direccion)  # Remover caracteres especiales
    for frase, abreviatura in transformaciones.items():
        direccion = re.sub(r'\b' + re.escape(frase) + r'\b', abreviatura, direccion)
    direccion = re.sub(r'\s+', ' ', direccion).strip()
    return direccion

# Función para obtener los segmentos de la dirección
def obtener_segmentos(direccion, prioridades):
    guiones = [m.start() for m in re.finditer('-', direccion)]
    if len(guiones) == 1:
        match = re.search(r'-\s*(\d+)', direccion)
        if match:
            parte_inicial = direccion[:match.end()].strip()
            parte_final = None
            for criterio in prioridades:
                criterio_pos = direccion.find(criterio, match.end())
                if criterio_pos != -1:
                    parte_final = direccion[criterio_pos:].strip()
                    break
            return parte_inicial, parte_final
    elif len(guiones) > 1:
        matches = list(re.finditer(r'-\s*(\d+)', direccion))
        if len(matches) > 1:
            match = matches[1]
            parte_inicial = direccion[:match.end()].strip()
            parte_final = None
            for criterio in prioridades:
                criterio_pos = direccion.find(criterio, match.end())
                if criterio_pos != -1:
                    parte_final = direccion[criterio_pos:].strip()
                    break
            return parte_inicial, parte_final
    return direccion, None

# Función para reordenar la dirección
def reordenar_direccion(direccion):
    prioridad = {'TO': 1, 'SO': 40, 'AP': 80, 'LC': 81, 'HB': 82,
                 'PQ': 120, 'DP': 121, 'PQSM': 122, 'SOPQ': 123, 'OF': 124, 'CA': 125}

    elementos = re.findall(r'\b(TO|AP|LC|HB|SO|PQ|DP|PQSM|SOPQ|OF|CA)\b\s*([A-Z0-9\-]*)', direccion)
    elementos_procesados = [(elem[0], elem[1].replace('-', '_')) for elem in elementos]
    elementos_ordenados = sorted(elementos_procesados, key=lambda x: prioridad.get(x[0], 8))

    direccion_reordenada = re.sub(r'\b(TO|AP|LC|HB|SO|PQ|DP|PQSM|SOPQ|OF|CA)\b\s*[A-Z0-9-]*', '', direccion).strip()
    direccion_reordenada = re.sub(r'\s+', ' ', direccion_reordenada)

    for elem in elementos_ordenados:
        direccion_reordenada += f' {elem[0]} {elem[1]}'

    return direccion_reordenada.strip()

# Aplicar la normalización y las funciones adicionales a cada registro
prioridades = ['TO', 'AP', 'LC', 'HB', 'SO', 'PQ', 'DP', 'PQSM', 'SOPQ', 'OF', 'CA']

# Aplicar transformaciones de frases primero y luego de palabras
data['direccion_normalizada'] = data['direccion'].apply(lambda x: normalizar_direccion(x, transformaciones_frases))
data['direccion_normalizada'] = data['direccion_normalizada'].apply(lambda x: normalizar_direccion(x, transformaciones_word))

# Reordenar dirección final
data["direccion_final"] = data["direccion_normalizada"].apply(reordenar_direccion)

# Añadir 'parte_inicial' y 'parte_final'
data['parte_inicial'], data['parte_final'] = zip(*data['direccion_final'].apply(lambda x: obtener_segmentos(x, prioridades)))

# Leer el archivo de transformaciones para parte_final
transformaciones_parte_final_df = pd.read_csv('transformaciones_parte_final.dic').dropna()
transformaciones_parte_final_df.columns = transformaciones_parte_final_df.columns.str.strip()
transformaciones_parte_final_df['frase'] = transformaciones_parte_final_df['frase'].astype(str)
transformaciones_parte_final_df['abreviatura'] = transformaciones_parte_final_df['abreviatura'].astype(str)
transformaciones_parte_final = dict(sorted(transformaciones_parte_final_df[['frase', 'abreviatura']].values, key=lambda x: len(x[0]), reverse=True))

# Función de normalización para parte_final
def normalizar_parte_final(parte_final, transformaciones):
    if parte_final is None:
        return parte_final
    parte_final = parte_final.upper()
    for frase, abreviatura in transformaciones.items():
        parte_final = re.sub(r'\b' + re.escape(frase) + r'\b', abreviatura, parte_final)
    parte_final = re.sub(r'\s+', ' ', parte_final).strip()
    return parte_final

# Aplicar normalización de parte_final
data['parte_final'] = data['parte_final'].apply(lambda x: normalizar_parte_final(x, transformaciones_parte_final))
