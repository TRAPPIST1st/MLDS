# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 15:07:30 2024

@author: SENA
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
  
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier

#CARGAR DATABASE Y CREAR DATAFRAME
file_path = "iris.csv"
df = pd.read_csv(file_path)

#ELIMINAR COLUMNA ID
df = df.drop(columns=['Id'])

#DESCRIPCION BASICA DEL DATAFRAME
print("Descripcion estadistica del dataframe ")
print (df.describe())

#MOSTRAR NUMERO DE MUESTRAS POR ESPECIE 
print ("\nNumero de muestras por especie")
print (df["Species"]. value_counts())

#HISTOGRAMA DE LAS VARIABLES NUMERICAS
df.hist(edgecolor="black",linewidth=1.2,figsize=(10, 8))
plt.suptitle("distribucion de las variables del conjunto iris",fontsize=16)
plt.show()

#GRAFICO DE CAJA (BOXPLOT) PARA CADA CARACTERISTICA SEGUN LA ESPECIE
plt.figure(figsize=(12,6))
sns.boxplot(data=df, x="Species",y="SepalLengthCm")
plt.title("Boxplot de SepalLength por Especie")
plt.show()

# """
#clasificadores
#"""
X = np.array(df.drop(['Species'], axis = 1))
y = np.array(df['Species'])

#separo los datos de train en entrenamiento y prueba para probar algoritmos
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.3)
print ('son {} datos para entrenamiento y {} datos para prueba'.format(X_train.shape[0], X_test.shape[0]))

#MODELO REGRESION LOGISTICA
algoritmo = LogisticRegression(max_iter=200) #AÑADIR MAX ITER PARA EVITAR ADVERTENCIAS DE CONVERGENCIA
algoritmo.fit(X_train, y_train)
Y_pred = algoritmo.predict(X_test)
print('precisión Regresión Logistica:{}'.format(algoritmo.score(X_train, y_train)))
