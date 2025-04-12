# -*- coding: utf-8 -*-
"""
Created on Sun Mar  9 23:49:26 2025

@author: TRAPPIST
"""

from bs4 import BeautifulSoup
import requests

URL = "https://psicologiaymente.com/reflexiones/frases-famosas"  # Reemplaza con la URL de interés
page = requests.get(URL)

# Analizar el HTML
soup = BeautifulSoup(page.content, "html.parser")

# Extraer el primer título h1
titulo = soup.find("h1").text
print("Título de la página:", titulo)

# Extraer todos los párrafos <p>
parrafos = soup.find_all("h3")
for i, p in enumerate(parrafos, start=1):
    print(f"Párrafo {i}: {p.text}")
