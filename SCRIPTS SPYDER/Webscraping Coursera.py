# -*- coding: utf-8 -*-
"""
Created on Sun Mar  9 23:18:49 2025

@author: TRAPPIST
"""
#ANTES DE TODO, VERIFICAR EL ARCHIVO ROBOTS.EXE PARA VER SI EL WEBSCRAPING ES LEGAL

"""
BeautifulSoup: BeautifulSoup es una biblioteca de Python que se utiliza con fines 
de web scraping para extraer datos de archivos HTML y XML. 
Crea un árbol de análisis a partir del código fuente de la página 
que se puede utilizar para extraer datos de una manera jerárquica y más legible.
"""
from bs4 import BeautifulSoup
import requests
URL = "https://en.wikipedia.org/wiki/List_of_countries_by_suicide_rate"
page = requests.get(URL)
soup = BeautifulSoup(page.content, "html.parser")

"""
Scrapy: Scrapy es un marco de trabajo de rastreo web colaborativo
 y de código abierto para Python. Se utiliza para extraer datos del sitio web.
 """
 
import scrapy
class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ['https://en.wikipedia.org/wiki/List_of_countries_by_suicide_rate',]
    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {'quote': quote.css('span.text::text').get()}
            
"""
Selenium: Selenium es una herramienta utilizada para controlar navegadores web 
a través de programas y automatizar tareas del navegador.
"""
from selenium import webdriver
driver = webdriver.Firefox()
driver.get("https://en.wikipedia.org/wiki/List_of_countries_by_suicide_rate")

"""
El web scraping se utiliza en varios campos y tiene muchas aplicaciones:
Comparación de precios: servicios como ParseHub utilizan el web scraping 
para recopilar datos de sitios web de compras en línea y los utilizan para
 comparar los precios de los productos.

Recopilación de direcciones de correo electrónico:
muchas empresas que utilizan el correo electrónico como medio de marketing
utilizan el web scraping para recopilar direcciones de correo electrónico y 
luego enviar correos electrónicos masivos.

Scraping de redes sociales: el web scraping se utiliza para recopilar datos de sitios web 
de redes sociales como Twitter para averiguar qué es tendencia.
"""