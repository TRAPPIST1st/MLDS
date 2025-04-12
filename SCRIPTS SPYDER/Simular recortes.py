# -*- coding: utf-8 -*-
"""
Created on Sat Mar  1 09:06:53 2025

@author: APRENDIZ
"""

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

def crop_center(image_path, output_path, crop_size=100):
    """
    Recorta una imagen en el centro con un tamaño cuadrado de 100 píxeles,
    muestra la matriz de la imagen y sus componentes RGB.
    
    :param image_path: Ruta de la imagen de entrada.
    :param output_path: Ruta donde se guardará la imagen recortada.
    :param crop_size: Tamaño del recorte cuadrado (100x100 píxeles por defecto).
    """
    # Cargar la imagen desde la ruta especificada
    image = Image.open(image_path)
    
    # Obtener las dimensiones originales de la imagen
    img_width, img_height = image.size
    
    # Calcular las coordenadas del recorte centrado
    left = (img_width - crop_size) // 2
    top = (img_height - crop_size) // 2
    right = left + crop_size
    bottom = top + crop_size
    
    # Realizar el recorte
    cropped_image = image.crop((left, top, right, bottom))
    
    # Convertir la imagen recortada en matriz numpy
    cropped_array = np.array(cropped_image)
    
    # Separar los canales RGB
    R = cropped_array[:, :, 0]  # Canal Rojo
    G = cropped_array[:, :, 1]  # Canal Verde
    B = cropped_array[:, :, 2]  # Canal Azul
    
    # Mostrar la imagen recortada
    plt.figure(figsize=(10, 5))
    
    plt.subplot(1, 4, 1)
    plt.imshow(cropped_image)
    plt.title("Imagen Recortada")
    plt.axis("off")
    
    plt.subplot(1, 4, 2)
    plt.imshow(R, cmap="Reds")
    plt.title("Canal Rojo")
    plt.axis("off")
    
    plt.subplot(1, 4, 3)
    plt.imshow(G, cmap="Greens")
    plt.title("Canal Verde")
    plt.axis("off")
    
    plt.subplot(1, 4, 4)
    plt.imshow(B, cmap="Blues")
    plt.title("Canal Azul")
    plt.axis("off")
    
    plt.show()
    
    # Guardar la imagen recortada en la ruta final
    cropped_image.save(output_path)
    
    print(f"Imagen recortada guardada en: {output_path}")

# Definir la ruta de entrada y salida
input_path = "C:\imagenes\imagen.jpg"
output_path = "C:\imagenes\imagen2.jpg"

# Definir el tamaño del recorte cuadrado (100x100 píxeles)
crop_size = 500

# Llamar a la función para recortar la imagen
crop_center(input_path, output_path, crop_size)