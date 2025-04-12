# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 18:43:34 2024

@author: fabio
"""

import os
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder

def upload():
    # Definir la ruta de la carpeta principal donde se encuentran las imágenes para el entrenamiento
    ruta_imagenes = r"C:\Users\TRAPPIST\Desktop\machine learning\imagenes"
    # Definir la ruta de la carpeta donde se encuentra la imagen de prueba
    ruta_resultado = r"C:\Users\TRAPPIST\Desktop\machine learning\resultado"
    
    # Definir el tamaño al que redimensionaremos las imágenes
    tamaño = (64, 64)

    # Inicializar listas para almacenar las imágenes y las etiquetas
    imagenes = []
    etiquetas = []

    # Iterar a través de todas las subcarpetas en 'Imagenes'
    for carpeta_nombre in os.listdir(ruta_imagenes):
        carpeta_ruta = os.path.join(ruta_imagenes, carpeta_nombre)
        if not os.path.isdir(carpeta_ruta):
            continue

        # Procesar todas las imágenes en la subcarpeta actual
        for imagen_nombre in os.listdir(carpeta_ruta):
            imagen_ruta = os.path.join(carpeta_ruta, imagen_nombre)
            try:
                # Cargar la imagen y redimensionarla
                imagen = Image.open(imagen_ruta).resize(tamaño)
                # Convertir la imagen a un array y normalizarla
                array_imagen = np.array(imagen).flatten() / 255.0

                # Agregar la imagen y la etiqueta (nombre de la carpeta) a las listas
                imagenes.append(array_imagen)
                etiquetas.append(carpeta_nombre)
            except Exception as e:
                print(f"Error al procesar {imagen_ruta}: {e}")

    # Convertir las listas en arrays de numpy
    X = np.array(imagenes)
    y = np.array(etiquetas)

    # Comprobar que X e y no estén vacíos antes de continuar
    if X.size == 0 or y.size == 0:
        print("No se encontraron imágenes o etiquetas para el entrenamiento.")
        return

    # Codificar las etiquetas como números
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)

    # Dividir los datos en conjuntos de entrenamiento y prueba
    x_entrenamiento, x_prueba, y_entrenamiento, y_prueba = train_test_split(X, y, test_size=0.2, random_state=42)

    # Entrenar el modelo SVM
    modelo = SVC(kernel='linear')
    modelo.fit(x_entrenamiento, y_entrenamiento)

    # Evaluar el modelo
    porcentaje_acierto = modelo.score(x_prueba, y_prueba)
    print("Porcentaje de acierto del modelo:", porcentaje_acierto)

    # Intentar predecir la etiqueta de una nueva imagen en la carpeta 'Resultado'
    ruta_nueva_imagen = os.path.join(ruta_resultado, "45.jpg")
    try:
        imagen_nueva = Image.open(ruta_nueva_imagen).resize(tamaño)
        array_nueva_imagen = np.array(imagen_nueva).flatten() / 255.0

        # Predecir la etiqueta de la nueva imagen
        etiqueta_predicha = modelo.predict([array_nueva_imagen])[0]
        etiqueta_predicha = label_encoder.inverse_transform([etiqueta_predicha])[0]
        print("Etiqueta predicha para la nueva imagen:", etiqueta_predicha)
    except Exception as e:
        print(f"Error al predecir la nueva imagen: {e}")

# Llamar a la función
upload()
