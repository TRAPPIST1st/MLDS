# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 08:02:19 2024

@author: SENA
"""

import pandas as pd
transformaciones_word_df = pd.read_csv('transformaciones_word.dic')
# Eliminar valores nulos y convertir a cadenas para transformaciones de palabras
transformaciones_word_df = transformaciones_word_df.dropna()
transformaciones_word_df.columns = transformaciones_word_df.columns.str.strip()  # Eliminar espacios en blanco en los nombres de las columnas
transformaciones_word_df['palabra'] = transformaciones_word_df['palabra'].astype(str)
transformaciones_word_df['abreviatura'] = transformaciones_word_df['abreviatura'].astype(str)
########
transformaciones_word = dict(zip(transformaciones_word_df['palabra'] , transformaciones_word_df['abreviatura']))
