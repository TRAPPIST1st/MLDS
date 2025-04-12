# -*- coding: utf-8 -*-
"""
Created on Fri Oct 11 20:55:54 2024

@author: TRAPPIST
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

file_path = "DatosSeguros.csv"
df = pd.read_csv(file_path)

# Eliminar valores nulos 
df = df.dropna()
df.columns = df.columns.str.strip()
df['edad'] = df['edad'].astype(str)
df['sexo'] = df['sexo'].astype(str)
df['imc'] = df['imc'].astype(str)
df['hijos'] = df['hijos'].astype(str)
df['fumador'] = df['fumador'].astype(str)
df['region'] = df['region'].astype(str)
df['valor_seguro'] = df['valor_seguro'].astype(str)

# Reemplazar 'yes' por 'si' en la columna deseada
df['fumador'] = df['fumador'].replace('yes', 'si')

#ELIMINAR "." DE LA COLUMNA VALOR_SEGURO
df['valor_seguro'] = df['valor_seguro'].str.replace('.', '', regex=False)

"""
#CONVERTIR COLUMNA EN NUMERICA PARA OPERACIONES MATEMATICAS (SOLO SI SE NECESITA)
df['valor_seguro'] = pd.to_numeric(df['valor_seguro'])
"""

#DESCRIPCION BASICA DEL DATAFRAME
print("Descripcion estadistica del dataframe ")
print (df.describe())

#MOSTRAR NUMEROS DE LOS DATOS DE LAS COLUMNAS EN TOTAL
print ("\nNumero de EDADES")
print (df["edad"]. value_counts())

print ("\nNumero de SEXOS")
print (df["sexo"]. value_counts())

print ("\nNumero de IMC")
print (df["imc"]. value_counts())

print ("\nNumero de HIJOS")
print (df["hijos"]. value_counts())

print ("\nNumero de FUMADORES")
print (df["fumador"]. value_counts())

print ("\nNumero de REGIONES")
print (df["region"]. value_counts())

print ("\nVALOR SEGUROS")
print (df["valor_seguro"]. value_counts())

# Convertir todas las columnas de tipo objeto (texto) a mayúsculas
df = df.apply(lambda x: x.str.upper() if x.dtype == "object" else x)

# Convertir las columnas numéricas a tipo float si es necesario

df['edad'] = pd.to_numeric(df['edad'])
df['imc'] = pd.to_numeric(df['imc'])
df['hijos'] = pd.to_numeric(df['hijos'])
df['valor_seguro'] = pd.to_numeric(df['valor_seguro'])

# Crear el histograma de las variables numéricas
df.hist(edgecolor="black", linewidth=1.2, figsize=(10, 8))
plt.suptitle("Distribución de las variables numéricas", fontsize=16)
plt.show()

# Crear el gráfico de caja
plt.figure(figsize=(12, 6))
sns.boxplot(data=df, x="edad", y="hijos")  # Cambia "sexo" y "imc" por las columnas que desees comparar
plt.title("Boxplot de edad según Hijos")
plt.xlabel("edad")
plt.ylabel("hijos")
plt.show()

# Crear un pairplot
sns.pairplot(df, hue="edad")  # Cambia "sexo" por la columna categórica que desees usar
plt.suptitle("Gráfico de dispersión de pares por edad", y=1.02)
plt.show()

sns.pairplot(df, hue="hijos")  # Cambia "sexo" por la columna categórica que desees usar
plt.suptitle("Gráfico de dispersión de pares por hijos", y=1.02)
plt.show()

# Guardar los cambios de nuevo en un archivo CSV si es necesario
df.to_csv('datafumadores_normalizada.csv', index=False)