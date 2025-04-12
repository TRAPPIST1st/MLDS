# -*- coding: utf-8 -*-
"""
Created on Sat Mar  1 10:50:50 2025

@author: TRAPPIST
"""

import os
import numpy as np
import cv2
import matplotlib.pyplot as plt
from sklearn.neighbors import KNeighborsRegressor
from sklearn.model_selection import train_test_split

def crop_random_patches(image_path, output_folder, crop_size=10, num_patches=500):
    """
    Extrae recortes aleatorios de una imagen y los guarda en una carpeta.
    
    :param image_path: Ruta de la imagen de entrada.
    :param output_folder: Carpeta donde se guardarán los recortes.
    :param crop_size: Tamaño del recorte cuadrado (10x10 píxeles por defecto).
    :param num_patches: Número de recortes aleatorios.
    :return: Coordenadas y recortes en formato NumPy array.
    """
    os.makedirs(output_folder, exist_ok=True)
    image = cv2.imread(image_path)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convertir a RGB
    img_height, img_width, _ = image.shape
    
    patches = []
    positions = []
    
    for i in range(num_patches):
        left = np.random.randint(0, img_width - crop_size)
        top = np.random.randint(0, img_height - crop_size)
        
        patch = image[top:top+crop_size, left:left+crop_size]  # Extraer parche
        patch_array = patch.flatten()  # Convertir a vector 1D
        
        cv2.imwrite(os.path.join(output_folder, f"patch_{i}.png"), cv2.cvtColor(patch, cv2.COLOR_RGB2BGR))
        
        patches.append(patch_array)
        positions.append([left, top])
    
    # Convertir listas a numpy arrays y asegurar enteros
    positions = np.array(positions, dtype=np.int32)
    patches = np.array(patches, dtype=np.float32)
    
    return positions, patches, image.shape

def reconstruct_with_patches(image_shape, positions, patches, crop_size=10):
    """
    Reconstruye la imagen colocando los recortes en sus ubicaciones reales.
    
    :param image_shape: Dimensiones originales de la imagen.
    :param positions: Coordenadas de los recortes.
    :param patches: Contenido de los recortes.
    :param crop_size: Tamaño del recorte.
    """
    img_height, img_width, _ = image_shape
    reconstructed = np.zeros((img_height, img_width, 3), dtype=np.uint8)
    
    for i, pos in enumerate(positions):
        x, y = int(pos[0]), int(pos[1])  # Asegurar enteros
        patch = patches[i].reshape((crop_size, crop_size, 3)).astype(np.uint8)
        reconstructed[y:y+crop_size, x:x+crop_size] = patch
    
    return reconstructed

def train_and_predict(positions, patches, image_shape, crop_size=10):
    """
    Entrena un modelo KNN con los recortes disponibles y predice en posiciones faltantes.
    
    :param positions: Coordenadas de los recortes.
    :param patches: Contenido de los recortes.
    :param image_shape: Dimensiones originales de la imagen.
    :param crop_size: Tamaño del recorte.
    """
    img_height, img_width, _ = image_shape
    
    # Dividir datos en entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(positions, patches, test_size=0.2, random_state=42)
    
    # Entrenar modelo KNN
    knn = KNeighborsRegressor(n_neighbors=5, weights='distance')
    knn.fit(X_train, y_train)
    
    # Crear imagen reconstruida
    reconstructed = np.zeros((img_height, img_width, 3), dtype=np.uint8)
    
    # Colocar los recortes originales
    for i, pos in enumerate(positions):
        x, y = int(pos[0]), int(pos[1])
        patch = patches[i].reshape((crop_size, crop_size, 3)).astype(np.uint8)
        reconstructed[y:y+crop_size, x:x+crop_size] = patch
    
    # Generar coordenadas faltantes para predicción
    missing_positions = []
    for y in range(0, img_height - crop_size, crop_size):
        for x in range(0, img_width - crop_size, crop_size):
            if not any(np.array_equal([x, y], p) for p in positions):
                missing_positions.append([x, y])
    
    missing_positions = np.array(missing_positions, dtype=np.int32)
    
    # Predecir los recortes faltantes
    if len(missing_positions) > 0:
        predicted_patches = knn.predict(missing_positions)
        
        for i, pos in enumerate(missing_positions):
            x, y = int(pos[0]), int(pos[1])
            patch = predicted_patches[i].reshape((crop_size, crop_size, 3)).astype(np.uint8)
            reconstructed[y:y+crop_size, x:x+crop_size] = patch
    
    # Mostrar imagen reconstruida
    plt.imshow(reconstructed)
    plt.title("Imagen Reconstruida con Predicción de Recortes Faltantes")
    plt.axis("off")
    plt.show()
    
    return reconstructed

# Definir rutas
input_path = r"C:\Users\TRAPPIST\Desktop\ModeloForense\mujer.jpg"
output_folder = r"C:\Users\TRAPPIST\Desktop\ModeloForense\mujerCarpeta.jpg"

# Generar recortes
positions, patches, image_shape = crop_random_patches(input_path, output_folder)

# Reconstruir la imagen colocando solo los recortes en sus posiciones reales
reconstructed_patches_image = reconstruct_with_patches(image_shape, positions, patches)
cv2.imwrite(r"C:\Users\TRAPPIST\Desktop\ModeloForense\mujer_reconstruida.jpg", cv2.cvtColor(reconstructed_patches_image, cv2.COLOR_RGB2BGR))

# Entrenar modelo y predecir en coordenadas faltantes
reconstructed_final = train_and_predict(positions, patches, image_shape)
cv2.imwrite(r"C:\Users\TRAPPIST\Desktop\ModeloForense\mujer_reconstruida.jpg", cv2.cvtColor(reconstructed_final, cv2.COLOR_RGB2BGR))