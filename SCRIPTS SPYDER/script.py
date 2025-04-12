# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 08:21:20 2024

@author: SENA
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import silhouette_score
import joblib

#CARGAR DATOS

file_path = 'entrega_ml.csv'
data = pd.read_csv(file_path)
data ["text"] = data.apply(lambda row: " ".join(row.values.astype(str)), axis=1)

#CONVERTIR EL TEXTO EN CARACTERISTICAS NUMERICAS USANDO TF - IDF
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data['text'])
#INICIO PARA TRABAJAR CON EL VECTORIZER  PARA CONFIGURACION DE DICCIONARIOS
#GUARDAR EL VECTORIZADOR DE UN ARCHIVO
vectorizer_file = 'TfidfVectorizer.pkl'
joblib.dump(vectorizer,vectorizer_file)
print (f"vectorizador TF-IDF guardado en {vectorizer_file}")

#CONVERTIR MATRIZ TD-IDF A UN DATAFRAME PARA MEJOR VISUALIZACION
tfidf_matrix = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())
print ("matriz. TF-IDF:")
print (tfidf_matrix.head())

#GUARDAR LA MATRIZ TF-IDF EN UN ARCHIVO CSV PARA REFERENCIA
tfidf_matrix.to_csv('tfidf_matrix.csv', index=False)
print ("Matriz TF-IDF guardada en 'tfidf_matrix.csv'")

df = pd.read_csv('tfidf_matrix.csv', header=None)
datatrans = df.to_string (index=False,header=False).replace(',','\n')
with open ('tfidf_matrix_transf.csv','w',encoding='UTF-8') as file:
    file.write(datatrans)
    
#DEFINIR EL RANGO DE CLUSTERS A EVALUAR
start, end =2, 15 #DEFINIENDO RANGO DE CLUSTERS

#CALCULAR SILHOUETTE SCORE PARA DIFERENTES NUMEROS DE CLUSTERS
silhouette_scores = []
for k in range(start, end +1):  # Empezamos en 2 porque 1 cluster no tiene sentido calcular silueta
    kmeans = KMeans(n_clusters=k, n_init=15, random_state=0).fit(X)
    score = silhouette_score(X, kmeans.labels_)
    silhouette_scores.append(score)
    
#GRAFICAR EL SILHOUETTE SCORE
plt.figure(figsize=(8, 5))
sns.lineplot(x=range(start, end + 1), y=silhouette_scores, marker='o')
plt.title('silhouette score para encontrar el numero optimo de clusters comuna 04')
plt.xlabel('Número de clusters')
plt.ylabel('silhouette score')
plt.show()



#SI NO FUNCIONA EJECUTAR ABAJO
import matplotlib.pyplot as plt
import seaborn as sns

# Calcular silhouette_scores (supongo que ya lo hiciste)

# Limpiar cualquier figura anterior
plt.clf()  # Limpia la figura actual, opcional si solo tienes un gráfico

# Crear el gráfico deseado
plt.figure(figsize=(8, 5))
sns.lineplot(x=range(start, end + 1), y=silhouette_scores, marker='o')
plt.title('Silhouette Score para encontrar el número óptimo de clusters - Comuna 04')
plt.xlabel('Número de clusters')
plt.ylabel('Silhouette Score')
plt.show()
