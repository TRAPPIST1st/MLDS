# -*- coding: utf-8 -*-
"""
Created on Sun Mar  9 23:26:57 2025

@author: TRAPPIST
"""
#VERIFICAR ROBOTS.txt
#ESTE METODO ES PARA HACER WEBSCRAPING DE TABLAS
#CONTAR NUMERO DE TABLAS MANUAL PARA SABER QUE TABLA ESCOGER
#PROBABLEMENTE NECESITEN LIMPIEZA DEBIDO A LOS HIPERVINCULOS QUE QUEDAN REGISTRADOS



import pandas as pd
URL = 'https://en.wikipedia.org/wiki/List_of_countries_by_suicide_rate'
tables = pd.read_html(URL)
df = tables[2]
print(df)


import pandas as pd
URL = 'https://en.wikipedia.org/wiki/List_of_countries_by_GDP_(nominal)'
tables = pd.read_html(URL)
df = tables(2) # the required table will have index 2
print(df)