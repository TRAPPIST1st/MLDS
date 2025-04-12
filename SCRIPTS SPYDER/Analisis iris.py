# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 15:07:30 2024

@author: SENA
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

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