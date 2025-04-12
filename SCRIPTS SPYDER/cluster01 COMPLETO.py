# -*- coding: utf-8 -*-
"""
Created on Mon Sep 16 09:04:56 2024

@author: SENA
"""

# -- coding: utf-8 --
"""
Created on Mon Aug 26 07:56:04 2024

@author: SENA
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
import joblib

file_path = 'entrega_ml.csv'
data = pd.read_csv(file_path)
data['text'] = data.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)

# Convertir el texto en caracteristicas numericos usando TF-IDF
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data['text'])
# **INICIO PARA TRABAJAR CON EL VECTORIZER PARA CONFIGURACION DE DICCIONARIOS
# Guardar el Vectorizador en un archivo

vectorizer_file = "tfidf_vectorizer.pkl"
joblib.dump(vectorizer, vectorizer_file)
print(f"Vectorizador TF-IDF guardado en {vectorizer_file}")

# Convertir la matriz TF-IDf a un DataFrame para mejor visualizacion
tfidf_matrix = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())
print("Matriz TF-IDF:")
print(tfidf_matrix.head())

# Guardar la matriz TF-IDF en un archivo CSV para referencia
tfidf_matrix.to_csv('tfidf_matrix.csv', index=False)
print("Matriz TF-IDF guardada en 'tfidf_matrix.csv'")

df = pd.read_csv('tfidf_matrix.csv', header=None)
datatrans = df.to_string(index=False,header=False).replace(',','\n')
with open('tfidf_matrix_transf.scv','w' ,encoding='UTF-8') as file:
    file.write(datatrans)

#-------------------------------------------------------------------------------
import pandas as pd
import re
data = pd.read_csv('entrega_ml.csv')

# Leer los archivos CSV de transformaciones
transformaciones_frases_df = pd.read_csv('transformaciones_frases.dic')
transformaciones_word_df = pd.read_csv('transformaciones_word.dic')

# Eliminar valores nulos 
transformaciones_frases_df = transformaciones_frases_df.dropna()
transformaciones_frases_df.columns = transformaciones_frases_df.columns.str.strip()
transformaciones_frases_df['frase'] = transformaciones_frases_df['frase'].astype(str)
transformaciones_frases_df['abreviatura'] = transformaciones_frases_df['abreviatura'].astype(str)

transformaciones_word_df = transformaciones_word_df.dropna()
transformaciones_word_df.columns = transformaciones_word_df.columns.str.strip()
transformaciones_word_df['palabra'] = transformaciones_word_df['palabra'].astype(str)
transformaciones_word_df['abreviatura'] = transformaciones_word_df['abreviatura'].astype(str)

transformaciones_frases = dict(zip(transformaciones_frases_df['frase'], transformaciones_frases_df['abreviatura']))
transformaciones_word = dict(zip(transformaciones_word_df['palabra'], transformaciones_word_df['abreviatura']))

transformaciones_frases = dict(sorted(transformaciones_frases.items(), key=lambda item: len(item[0]), reverse=True))
transformaciones_word = dict(sorted(transformaciones_word.items(), key=lambda item: len(item[0]), reverse=True))

#Función de procesar guiones
def procesar_guiones(direccion):
    partes - direccion.split ('-')
    if len(partes) > 1:
        direccion = partes [0] + '-' + ' '.join(partes[1]).replace('-',' ')
        return direccion 
    
# Función de normalización de la dirección

def normalizar_direccion(direccion, transformaciones):
    direccion = direccion.upper()
    # Corrección aquí
    direccion = re.sub(r'[^A-Z0-9\s\-#]', '', direccion)
    
    # Aplicar transformaciones
    for frase, abreviatura in transformaciones.items():
        direccion = re.sub(r'\b' + re.escape(frase) + r'\b', abreviatura, direccion)
        
    direccion = re.sub(r'\s+', ' ', direccion).strip()
    return direccion

#funcion para obtener las partes de la dirección
def obtener_segmentos(direccion,prioridades):
    guiones - [m.start() for m in re.finditer('-', direccion)]
    if len(guiones) == 1:
        match = re.search (r'-\s*(\d+)',direccion)
        if match:
            parte_inicial = direccion [:match.end()].strip()
            parte_final = None
            for criterio in prioridades:
                criterio_pos = direccion.find(criterio, match.end())
                if criterio_pos != -1:
                    parte_final = direccion [criterio_pos:].strip()
                    break
                return parte_inicial, parte_final
    elif len (guiones) > 1:
        matches = list (re.finditer(r'-\s*(\d+)', direccion))
        if len (matches) > 1:
            match = matches [1]
            parte_incial = direccion [:match.end()].strip()
            parte_final = None
            for criterio in prioridades:
                criterio_pos = direccion.find (criterio, match.end())
                if criterio_pos != -1:
                    parte_final = direccion [criterio_pos:].strip()
                    break
            return parte_inicial, parte_final
    return direccion, None

#funcion reordenar direccion
def reordenar_direccion (direccion):
    prioridad = {' TO ': 1, 
                 ' SO ': 40,
                 ' AP ': 80, ' LC ': 81 , ' HB ': 82,
                 ' PQ ': 120,' DP ': 121, ' PQSM ': 122, ' SOPQ ': 123, ' OF ':124, ' CA ': 125  }
    
    
    
#Buscar los elementos de prioridad con sus valores
elementos = re.findall (r'\b(TO/AP/LC/HB/SO/PQ/DP/PQSM/SOPQ/OF/CA)\b\s*([A-Z0-9\-]*)' direccion)

#procesar cada elemento para eliminar guiones si los tiene
elementos_procesados = [(elem[0], elem[1].replace('-', '_')) for elem in elementos]
elementos_ordenados = sorted (elementos_procesados, key=lambda x:prioridad.get(f' {x[0]}',8))
                                                                               
# Eliminar los elementos originales de la dirección
direccion_reordenada = re.sub(r'\b(TO|AP|Lc|HS|SQ|Po|DP|PQM|SQPO|OF|CA)\b\s*[A-Z0-9-]*', '', direccion).strip()
direccion_reordenada = re.sub(r'\s+', ' ', direccion_reordenada)

# Añadir los elementos ordenados a la dirección reordenada
for elem in elementos_ordenados:
    direccion_reordenada += f'{elem[0]} {elem[1]} '

# Eliminar espacios adicionales
direccion_reordenada = re.sub(r'\s+', ' ', direccion_reordenada).strip()
return direccion_reordenada

# Aplicar la normalización y las funciones adicionales a cada registro
prioridades = ['TO', 'AP', 'Lc', 'HS', 'SQ', 'Po', 'DP', 'SDOP', 'PQM', 'SQPO', 'OF', 'CA']

                                                                               
# Aplicar transformaciones de frases primero y luego de palabras
data['direccion_normalizada'] = data['direccion'].apply(lambda x: normalizar_direccion(x, transformaciones_frases))
data['direccion_normalizada'] = data['direccion_normalizada'].apply(lambda x: normalizar_direccion(x, transformaciones_word))

data["direccion_final"] = data ["direccion_normalizada"].apply(reordenar_direccion)


# Añadir 'parte_inicial' y 'parte_final'
data['parte_inicial'], data['parte_final'] = zip(*data['direccion_final'].apply(lambda x: obtener_segmentos(x, prioridades)))

# Leer el archivo de transformaciones para parte_final
transformaciones_parte_final = pd.read_csv('transformaciones_parte_final.dic')
transformaciones_parte_final_df = transformaciones_parte_final.dropna()
transformaciones_parte_final_df.columns = transformaciones_parte_final_df.columns.str.strip()
transformaciones_parte_final_df['frase'] = transformaciones_parte_final_df['frase'].astype(str)
transformaciones_parte_final_df['abreviatura'] = transformaciones_parte_final_df['abreviatura'].astype(str)
transformaciones_parte_final = dict(sorted(transformaciones_parte_final.values, key=lambda item: len(item[0]), reverse=True))

# Función de normalización para parte_final
def normalizar_parte_final(parte_final, transformaciones):
    if parte_final is None:
        return parte_final


