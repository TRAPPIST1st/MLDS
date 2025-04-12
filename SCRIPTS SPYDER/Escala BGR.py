# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 14:49:57 2025

@author: TRAPPIST
"""

import numpy as np
import matplotlib.pyplot as plt
import cv2

# 2. Leer una imagen como matriz en escala de grises como si fueran 3 matrices
image_path = r"C:\Users\TRAPPIST\Desktop\Forense\Jupiter.jpg"

# Leer la imagen en color
image = cv2.imread(image_path)

# Convertir a escala de grises
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Simular la imagen en 3 matrices duplicando la escala de grises
gray_3channel = np.stack([gray_image] * 3, axis=-1)

# Crear imágenes en escalas de colores
blue_image = np.zeros_like(image)
blue_image[:, :, 0] = gray_image  # Canal azul

green_image = np.zeros_like(image)
green_image[:, :, 1] = gray_image  # Canal verde

red_image = np.zeros_like(image)
red_image[:, :, 2] = gray_image  # Canal rojo

# Mostrar la imagen original y las modificadas
fig, ax = plt.subplots(1, 5, figsize=(20, 6))
ax[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
ax[0].set_title("Imagen Original")
ax[0].axis("off")

ax[1].imshow(gray_3channel, cmap='gray')
ax[1].set_title("Imagen en Escala de Grises como 3 Canales")
ax[1].axis("off")

ax[2].imshow(cv2.cvtColor(blue_image, cv2.COLOR_BGR2RGB))
ax[2].set_title("Escala de Azules")
ax[2].axis("off")

ax[3].imshow(cv2.cvtColor(green_image, cv2.COLOR_BGR2RGB))
ax[3].set_title("Escala de Verdes")
ax[3].axis("off")

ax[4].imshow(cv2.cvtColor(red_image, cv2.COLOR_BGR2RGB))
ax[4].set_title("Escala de Rojos")
ax[4].axis("off")

plt.show()
