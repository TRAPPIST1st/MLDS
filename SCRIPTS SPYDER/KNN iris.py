# -*- coding: utf-8 -*-
"""
Created on Fri Oct 25 14:18:39 2024

@author: 
"""
import warnings
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import matplotlib.pyplot as plt

# Suprimir advertencias específicas
warnings.filterwarnings("ignore", category=FutureWarning, module="sklearn")

# Paso 1: Cargar el archivo Iris.csv
df = pd.read_csv(r'C:\Users\SENA\Desktop\iris\Iris.csv')

# Paso 2: Eliminar las columnas 'Id' y 'Species'
df = df.drop(['Id', 'Species'], axis=1)

# Crear el target o etiqueta
y = pd.read_csv(r'C:\Users\SENA\Desktop\iris\Iris.csv')['Species']  # Variable objetivo

# Paso 3: Normalizar las características
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df)

# Paso 4: Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.45, random_state=42)

# Paso 5: Configurar los parámetros para GridSearchCV
param_grid = {'n_neighbors': range(1, 21)}  # Probar valores de n_neighbors de 1 a 20
knn = KNeighborsClassifier()

# Validación cruzada con GridSearchCV para encontrar el mejor número de vecinos
grid_search = GridSearchCV(knn, param_grid, cv=7, scoring='accuracy') #CV SON LOS KN
grid_search.fit(X_train, y_train)

# Mejor modelo encontrado
best_knn = grid_search.best_estimator_
print("Mejor número de vecinos (n_neighbors):", grid_search.best_params_['n_neighbors'])

# Paso 6: Entrenar el modelo con el mejor número de vecinos
best_knn.fit(X_train, y_train)

# Paso 7: Realizar predicciones y calcular la precisión
y_pred = best_knn.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print("Precisión del modelo:", accuracy)

# Paso 8: Matriz de confusión
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=best_knn.classes_, yticklabels=best_knn.classes_)
plt.xlabel('Predicción')
plt.ylabel('Realidad')
plt.title('Matriz de Confusión del Modelo KNN (Optimizado)')
plt.show()