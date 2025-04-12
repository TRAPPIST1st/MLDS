# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 13:35:11 2024

@author: TRAPPIST
"""

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, KBinsDiscretizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

# Cargar el archivo CSV
file_path = r'C:\Users\SENA\Desktop\SEGUROS\DatosSeguros.csv'
df = pd.read_csv(file_path)

# Eliminar filas con valores faltantes (NaN)
df = df.dropna()

# Codificación de variables categóricas (convierte letras en numeros para poder entrenar el modelo)
label_encoder = LabelEncoder()
df['sexo'] = label_encoder.fit_transform(df['sexo'])
df['fumador'] = label_encoder.fit_transform(df['fumador'])
df['region'] = label_encoder.fit_transform(df['region'])

# Convertir 'valor_seguro' en categorías discretas (bajo, medio, alto)
discretizer = KBinsDiscretizer(n_bins=3, encode='ordinal', strategy='uniform')
df['valor_seguro'] = discretizer.fit_transform(df[['valor_seguro']])

# Definir variables predictoras y objetivo
X = df.drop('valor_seguro', axis=1)
y = df['valor_seguro']

# Dividir los datos en conjuntos de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.5, random_state=42)

# Entrenar el modelo de clasificación
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Evaluar el modelo
y_pred = model.predict(X_test)
print(f'Accuracy: {accuracy_score(y_test, y_pred)}')
print(classification_report(y_test, y_pred))
