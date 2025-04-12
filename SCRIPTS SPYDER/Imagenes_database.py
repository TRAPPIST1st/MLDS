# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 19:11:04 2024

@author: TRAPPIST
"""

import os
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
import mysql.connector

def upload():
    # Definir la ruta de la carpeta principal donde se encuentran las imágenes para el entrenamiento
    ruta_imagenes = r"C:\Inteligencia Artificial\Imagenes"
    # Definir la ruta de la carpeta donde se encuentra la imagen de prueba
    ruta_resultado = r"C:\Inteligencia Artificial\Resultado\45.png"
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
    try:
        imagen_nueva = Image.open(ruta_resultado).resize(tamaño)
        array_nueva_imagen = np.array(imagen_nueva).flatten() / 255.0

        # Predecir la etiqueta de la nueva imagen
        etiqueta_predicha = modelo.predict([array_nueva_imagen])[0]
        etiqueta_predicha = label_encoder.inverse_transform([etiqueta_predicha])[0]
        print("Etiqueta predicha para la nueva imagen:", etiqueta_predicha)

        # Convertir la imagen a formato de bytes para almacenar en la base de datos
        imagen_nueva_bytes = Image.open(ruta_resultado).tobytes()

        # Conectar e insertar la imagen en la base de datos MySQL
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="imagenes"
        )
        
        cursor = conexion.cursor()
        sql = "INSERT INTO imagen (nombre, datos) VALUES (%s, %s)"
        valores = (str(etiqueta_predicha), imagen_nueva_bytes)

        # Ejecutar la inserción
        cursor.execute(sql, valores)
        conexion.commit()
        print("Imagen insertada correctamente en la base de datos.")

    except Exception as e:
        print("Error al conectar o insertar en la base de datos:", e)

    finally:
        # Cerrar la conexión a la base de datos
        if conexion.is_connected():
            cursor.close()
            conexion.close()

# Llamar a la función
upload()