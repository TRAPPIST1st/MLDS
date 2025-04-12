# -*- coding: utf-8 -*-
"""
Created on Fri Dec  6 21:19:18 2024

@author: TRAPPIST
"""

import pandas as pd
import numpy as np
import sklearn

# Cargar el dataset
data = pd.read_csv("C:/Users/TRAPPIST/Downloads/medicina.csv")

# Eliminar las columnas no relevantes
columns_to_drop = ['Previous_Medication', 'Recommended_Medication', 'Diet_Type', 'Smoking_History', 'Alcohol_Consumption']
data_cleaned = data.drop(columns=columns_to_drop)


from sklearn.preprocessing import LabelEncoder

# Codificar variables categóricas
categorical_columns = ['Fever_Severity', 'Gender', 'Diet_Type']
encoder = LabelEncoder()
for col in categorical_columns:
    data[col] = encoder.fit_transform(data[col])

# Opcional: Convertir columnas binarias como "No"/"Yes" a 0 y 1
binary_columns = ['Headache', 'Body_Ache', 'Fatigue', 'Chronic_Conditions', 'Allergies', 'Smoking_History', 'Alcohol_Consumption']
data[binary_columns] = data[binary_columns].replace({'No': 0, 'Yes': 1})


from sklearn.preprocessing import StandardScaler

# Seleccionar las columnas numéricas para el clustering
numerical_columns = ['Temperature', 'Age', 'BMI', 'Heart_Rate', 'Humidity', 'AQI']
data_scaled = StandardScaler().fit_transform(data[numerical_columns])



from sklearn.cluster import KMeans

# Determinar el número de clusters (k)
kmeans = KMeans(n_clusters=9, random_state=42)
kmeans.fit(data_scaled)

# Etiquetas de los clusters
data['Cluster'] = kmeans.labels_

# Ver los primeros resultados
print(data[['Temperature', 'Age', 'Cluster']].head())



from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

# Reducir las dimensiones a 2 para visualización
pca = PCA(n_components=2)
data_pca = pca.fit_transform(data_scaled)

# Graficar los clusters
plt.scatter(data_pca[:, 0], data_pca[:, 1], c=data['Cluster'], cmap='viridis')
plt.xlabel('Componente Principal 1')
plt.ylabel('Componente Principal 2')
plt.title('Clusters de pacientes')
plt.show()


from sklearn.metrics import silhouette_score

score = silhouette_score(data_scaled, data['Cluster'])
print(f"Silhouette Score: {score}")

#METODO DEL CODO

inertias = []
for k in range(1, 15):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(data_scaled)
    inertias.append(kmeans.inertia_)

# Graficar el método del codo
import matplotlib.pyplot as plt
plt.plot(range(1, 15), inertias, marker='o')
plt.xlabel('Número de Clusters')
plt.ylabel('Inercia')
plt.title('Método del Codo')
plt.show()

