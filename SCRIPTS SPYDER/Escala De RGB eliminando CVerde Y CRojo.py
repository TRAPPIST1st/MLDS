# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 14:47:20 2025

@author: TRAPPIST
"""

import numpy as np
import matplotlib.pyplot as plt
import cv2

# 2. Leer una imagen como matriz en escala de grises como si fueran 3 matrices
image_path = r"C:\Users\TRAPPIST\Downloads\sistema.jpg"

# Leer la imagen en color
image = cv2.imread(image_path)

# Convertir a escala de grises
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Simular la imagen en 3 matrices duplicando la escala de grises
gray_3channel = np.stack([gray_image] * 3, axis=-1)

# Crear una imagen con solo el canal azul
blue_channel = image.copy()
blue_channel[:, :, 1] = 0  # Eliminar el canal verde
blue_channel[:, :, 2] = 0  # Eliminar el canal rojo

# Mostrar la imagen original, la escala de grises y la escala de azules
fig, ax = plt.subplots(1, 3, figsize=(18, 6))
ax[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
ax[0].set_title("Imagen Original")
ax[0].axis("off")

ax[1].imshow(gray_3channel, cmap='gray')
ax[1].set_title("Imagen en Escala de Grises como 3 Canales")
ax[1].axis("off")

ax[2].imshow(blue_channel)
ax[2].set_title("Imagen en Escala de Azules")
ax[2].axis("off")

plt.show()
