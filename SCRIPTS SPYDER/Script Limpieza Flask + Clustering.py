# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 19:49:32 2025

@author: TRAPPIST
"""

from flask import Flask, request, send_file
import pandas as pd
from io import BytesIO
from sklearn.ensemble import IsolationForest
from textblob import TextBlob

app = Flask(__name__)

def correct_text(text):
    """
    Corrige errores ortográficos y gramaticales en un texto utilizando TextBlob.
    """
    try:
        # TextBlob.correct() devuelve una versión corregida del texto
        return str(TextBlob(text).correct())
    except Exception:
        # En caso de error, retorna el texto original
        return text

def clean_csv_data(file_stream):
    # Leer el CSV desde el stream recibido
    df = pd.read_csv(file_stream)
    
    # Eliminar duplicados
    df = df.drop_duplicates()
    
    # Procesar cada columna
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            # Rellenar valores faltantes en columnas numéricas con la mediana
            df[col].fillna(df[col].median(), inplace=True)
        else:
            # Para columnas de texto: rellenar valores faltantes y normalizar
            if df[col].mode().empty:
                df[col].fillna("", inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)
            # Normalización: quitar espacios y convertir a minúsculas
            df[col] = df[col].str.strip().str.lower()
            # Integrar corrección ortográfica para cada registro de texto
            df[col] = df[col].apply(lambda x: correct_text(x) if isinstance(x, str) else x)
    
    # Integración de IA: detección de outliers en columnas numéricas con Isolation Forest
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        if not df[col].empty:
            model = IsolationForest(contamination=0.05, random_state=42)
            preds = model.fit_predict(df[[col]])
            # Se conservan solo los registros considerados normales (predicción = 1)
            df = df[preds == 1]
    
    return df

@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            return "No se encontró el archivo en la solicitud.", 400
        
        file = request.files["file"]
        if file.filename == "":
            return "No se seleccionó ningún archivo.", 400
        
        # Procesar el archivo CSV y limpiarlo
        df_clean = clean_csv_data(file)
        
        # Guardar el DataFrame limpio en un buffer en memoria
        output = BytesIO()
        df_clean.to_csv(output, index=False)
        output.seek(0)
        
        # Enviar el archivo limpio para descarga
        return send_file(
            output,
            as_attachment=True,
            download_name="datos_limpios.csv",
            mimetype="text/csv"
        )
    
    # Formulario simple para subir el archivo CSV
    return '''
    <!doctype html>
    <html>
      <head>
        <title>Sube tu CSV para limpieza</title>
      </head>
      <body>
        <h1>Sube tu archivo CSV</h1>
        <form method="post" enctype="multipart/form-data">
          <input type="file" name="file" accept=".csv">
          <input type="submit" value="Limpiar y Descargar">
        </form>
      </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
