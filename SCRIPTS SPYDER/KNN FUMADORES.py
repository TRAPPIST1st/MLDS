# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 00:06:23 2024

@author: TRAPPIST
"""

import warnings
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler, LabelEncoder
import seaborn as sns
import matplotlib.pyplot as plt

# Suprimir advertencias específicas
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

# Cargar y preparar los datos
file_path = r'C:\Users\TRAPPIST\Desktop\CARPETA DATABASES\CSV\SEGUROS\DatosSeguros.csv'
df = pd.read_csv(file_path)

# Preprocesamiento de datos
df = df.dropna()  # Eliminar filas con valores faltantes

# Codificación de variables categóricas
label_encoder = LabelEncoder()
df['sexo'] = label_encoder.fit_transform(df['sexo'])
df['fumador'] = label_encoder.fit_transform(df['fumador'])
df['region'] = label_encoder.fit_transform(df['region'])

# Convertir 'valor_seguro' en categorías
# Se divide en tres categorías: 'bajo', 'medio', y 'alto'
df['valor_seguro'] = pd.qcut(df['valor_seguro'], q=3, labels=['bajo', 'medio', 'alto'])

# Definir características (X) y etiqueta (y)
X = df.drop(['valor_seguro'], axis=1)
y = df['valor_seguro']

# Normalizar las características
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.5, random_state=42)

# Configurar el modelo y GridSearchCV
param_grid = {'n_neighbors': range(1, 21)}  # Probar valores de n_neighbors de 1 a 20
knn = KNeighborsClassifier()

# Validación cruzada con GridSearchCV para encontrar el mejor número de vecinos
grid_search = GridSearchCV(knn, param_grid, cv=2, scoring='accuracy')
grid_search.fit(X_train, y_train)

# Mejor modelo encontrado
best_knn = grid_search.best_estimator_
print("Mejor número de vecinos (n_neighbors):", grid_search.best_params_['n_neighbors'])

# Entrenar el modelo con el mejor número de vecinos
best_knn.fit(X_train, y_train)

# Realizar predicciones y calcular la precisión
y_pred = best_knn.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Precisión del modelo:", accuracy)

# Matriz de confusión
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=best_knn.classes_, yticklabels=best_knn.classes_)
plt.xlabel('Predicción')
plt.ylabel('Realidad')
plt.title('Matriz de Confusión del Modelo KNN (Optimizado)')
plt.show()
