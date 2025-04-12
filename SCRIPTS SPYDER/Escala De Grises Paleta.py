# -*- coding: utf-8 -*-
"""
Created on Sat Feb 22 14:29:47 2025

@author: TRAPPIST
"""

import numpy as np
import matplotlib.pyplot as plt
import cv2

# 1. Crear una matriz y visualizarla en escala de grises
# Definimos una matriz de 10x10 con valores entre 0 y 255
gray_matrix = np.array([
    [i * 25 for i in range(10)] for j in range(10)
], dtype=np.uint8)

# Mostrar la matriz en escala de grises
plt.imshow(gray_matrix, cmap='gray')
plt.colorbar()
plt.title("Matriz en Escala de Grises")
plt.show()