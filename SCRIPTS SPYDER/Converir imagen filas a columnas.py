# -*- coding: utf-8 -*-
"""
Created on Sat Mar  1 09:56:47 2025

@author: APRENDIZ
"""

from PIL import Image

def rotate_image(image_path, output_path, angle=45):
    """
    Rota una imagen un número específico de grados y la muestra.
    
    :param image_path: Ruta de la imagen de entrada.
    :param output_path: Ruta donde se guardará la imagen rotada.
    :param angle: Ángulo de rotación en grados (por defecto, 45 grados).
    """
    # Cargar la imagen desde la ruta especificada
    image = Image.open(image_path)
    
    # Rotar la imagen
    rotated_image = image.rotate(angle, expand=True)
    
    # Mostrar la imagen rotada
    rotated_image.show()
    
    # Guardar la imagen rotada
    rotated_image.save(output_path)
    
    print(f"Imagen rotada guardada en: {output_path}")

# Definir la ruta de entrada y salida
input_path = "C:\imagenes\imagen.jpg"
output_path = "C:\imagenes\imagen2.jpg"

# Llamar a la función para rotar la imagen
rotate_image(input_path, output_path)