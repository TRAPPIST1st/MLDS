# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 19:54:47 2025

@author: TRAPPIST
"""

from flask import Flask, request, send_file
import pandas as pd
from io import BytesIO
from sklearn.ensemble import IsolationForest
import requests

app = Flask(__name__)

# Configuración para la API de Gemini (hipotético)
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyCz3t0hURGws2I2cjOS5FgH"  # Endpoint ficticio
GEMINI_API_KEY = "AIzaSyCz3t0hURGws2I2cjOS5FgH-3qra2BfTWo"  # Reemplaza con tu clave si la tienes

def generate_summary(text):
    """
    Envía el texto a la API de Gemini para que genere un resumen.
    Se asume que la API recibe JSON con el campo 'text' y retorna un JSON con 'summary'.
    """
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    try:
        response = requests.post(GEMINI_API_URL, json=payload, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data.get("summary", "")
    except Exception as e:
        print(f"Error generando resumen: {e}")
        return ""

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
            # Para columnas de texto: rellenar valores faltantes con la moda o cadena vacía
            if df[col].mode().empty:
                df[col].fillna("", inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)
            # Normalización: quitar espacios y convertir a minúsculas
            df[col] = df[col].str.strip().str.lower()
            
            # Integración con la API de Gemini:
            # Se crea una nueva columna con el resumen del contenido de cada registro.
            summary_col = col + "_summary"
            df[summary_col] = df[col].apply(lambda x: generate_summary(x) if isinstance(x, str) and x != "" else "")
    
    # Integración de IA: detección de outliers en columnas numéricas con Isolation Forest
    numeric_cols = df.select_dtypes(include="number").columns
    for col in numeric_cols:
        if not df[col].empty:
            model = IsolationForest(contamination=0.05, random_state=42)
            preds = model.fit_predict(df[[col]])
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
        
        # Procesar el archivo CSV y limpiarlo/enriquecerlo
        df_clean = clean_csv_data(file)
        
        # Guardar el DataFrame limpio en un buffer en memoria
        output = BytesIO()
        df_clean.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name="datos_enriquecidos.csv",
            mimetype="text/csv"
        )
    
    return '''
    <!doctype html>
    <html>
      <head>
        <title>Sube tu CSV para limpieza y enriquecimiento</title>
      </head>
      <body>
        <h1>Sube tu archivo CSV</h1>
        <form method="post" enctype="multipart/form-data">
          <input type="file" name="file" accept=".csv">
          <input type="submit" value="Procesar y Descargar">
        </form>
      </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
