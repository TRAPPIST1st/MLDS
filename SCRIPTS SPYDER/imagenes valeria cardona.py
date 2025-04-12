
# -*- coding: utf-8 -*-
"""
Created on Thu Dec  5 12:17:36 2024

@author: valeria cardona
"""

# -*- coding: utf-8 -*-
import os
import io
import numpy as np
import pymysql
from PIL import Image
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import LabelEncoder
import mysql.connector

def upload_and_train():
    # Definir rutas principales
    ruta_imagenes = r"C:\xampp\htdocs\Imagenes_modelo\machinelearning\imagenes"
    ruta_resultado = r"C:\xampp\htdocs\Imagenes_modelo\machinelearning\resultado\45.jpg"
    tamaño = (64, 64)

    # Mapear carpetas a tablas correspondientes
    tabla_map = {
        "gatos": "gatos",
        "mariposas": "mariposas", 
        "perros": "perros",
        "osos": "osos"
    }

    # Inicializar listas para almacenar imágenes y etiquetas
    imagenes = []
    etiquetas = []

    # Conectar a la base de datos con manejo de excepciones
    try:
        conexion = pymysql.connect(
            host="localhost",
            user="root",
            password="",  # Cambia si configuraste una contraseña
            database="imagenes"
        )
        cursor = conexion.cursor()

        # Procesar imágenes desde las carpetas
        for carpeta_nombre in os.listdir(ruta_imagenes):
            carpeta_ruta = os.path.join(ruta_imagenes, carpeta_nombre)

            # Validar carpeta
            if carpeta_nombre not in tabla_map:
                print(f"Carpeta ignorada (sin tabla asignada): {carpeta_nombre}")
                continue

            tabla = tabla_map[carpeta_nombre]
            columna_imagen = f"imagenes_{carpeta_nombre}"

            if not os.path.isdir(carpeta_ruta):
                continue

            for imagen_nombre in os.listdir(carpeta_ruta):
                imagen_ruta = os.path.join(carpeta_ruta, imagen_nombre)
                try:
                    # Procesar imagen con más robustez
                    with Image.open(imagen_ruta) as imagen:
                        imagen = imagen.convert('RGB').resize(tamaño)
                        
                        # Convertir imagen a bytes de manera eficiente
                        buffer = io.BytesIO()
                        imagen.save(buffer, format='jpg')
                        imagen_bytes = buffer.getvalue()

                        # Preparar array para entrenamiento
                        array_imagen = np.array(imagen).flatten() / 255.0

                        # Agregar a listas de entrenamiento
                        imagenes.append(array_imagen)
                        etiquetas.append(carpeta_nombre)

                        # Insertar imagen en la base de datos
                        sql = f"INSERT INTO {tabla} (nombre, {columna_imagen}) VALUES (%s, %s)"
                        valores = (imagen_nombre, imagen_bytes)
                        cursor.execute(sql, valores)
                        print(f"Imagen '{imagen_nombre}' insertada correctamente.")

                except Exception as e:
                    print(f"Error al procesar {imagen_ruta}: {str(e)}")

        # Confirmar cambios en la base de datos
        conexion.commit()

        # Convertir listas en arrays para entrenamiento
        X = np.array(imagenes)
        y = np.array(etiquetas)

        # Codificar etiquetas
        label_encoder = LabelEncoder()
        y = label_encoder.fit_transform(y)

        # Dividir datos en entrenamiento y prueba
        x_entrenamiento, x_prueba, y_entrenamiento, y_prueba = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Entrenar modelo SVM
        modelo = SVC(kernel='linear')
        modelo.fit(x_entrenamiento, y_entrenamiento)

        # Evaluar modelo
        porcentaje_acierto = modelo.score(x_prueba, y_prueba)
        print("Porcentaje de acierto del modelo:", porcentaje_acierto)

        # Intentar predecir con una nueva imagen
        imagen_nueva = Image.open(ruta_resultado).convert('RGB').resize(tamaño)
        array_nueva_imagen = np.array(imagen_nueva).flatten() / 255.0

        # Predecir etiqueta
        etiqueta_predicha = modelo.predict([array_nueva_imagen])[0]
        etiqueta_predicha = label_encoder.inverse_transform([etiqueta_predicha])[0]
        print("Etiqueta predicha para la nueva imagen:", etiqueta_predicha)

        # Insertar imagen de prueba en base de datos
        buffer_nueva = io.BytesIO()
        imagen_nueva.save(buffer_nueva, format='jpg')
        imagen_nueva_bytes = buffer_nueva.getvalue()

        tabla_predicha = tabla_map[etiqueta_predicha]
        columna_predicha = f"imagenes_{etiqueta_predicha}"

        sql = f"INSERT INTO {tabla_predicha} (nombre, {columna_predicha}) VALUES (%s, %s)"
        valores = ("nueva_imagen.jpg", imagen_nueva_bytes)
        cursor.execute(sql, valores)
        conexion.commit()
        print("Imagen de prueba insertada correctamente.")

    except mysql.connector.Error as err:
        print(f"Error de MySQL: {err}")
    except Exception as e:
        print(f"Error general: {str(e)}")
    finally:
        # Cerrar conexión a la base de datos
        if conexion:
            try:
                cursor.close()
                conexion.close()
                print("Conexión a la base de datos cerrada.")
            except mysql.connector.Error as err:
                print(f"Error al cerrar la conexión: {err}")

# Llamar a la función
upload_and_train()