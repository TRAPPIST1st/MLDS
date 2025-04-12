# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 14:30:51 2025

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

# Mostrar la imagen original y la modificada
fig, ax = plt.subplots(1, 2, figsize=(12, 6))
ax[0].imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
ax[0].set_title("Imagen Original")
ax[0].axis("off")

ax[1].imshow(gray_3channel, cmap='gray')
ax[1].set_title("Imagen en Escala de Grises como 3 Canales")
ax[1].axis("off")

plt.show()