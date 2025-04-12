# -*- coding: utf-8 -*-
"""
Created on Sat Mar 29 20:18:33 2025

@author: TRAPPIST
"""

from flask import Flask, request, send_file, render_template_string
import pandas as pd
from io import BytesIO
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

app = Flask(__name__)

# Plantilla HTML con Bootstrap para una interfaz más llamativa
HTML_TEMPLATE = '''
<!doctype html>
<html lang="es">
  <head>
    <meta charset="utf-8">
    <title>Procesador de CSV</title>
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
      body {
        background-color: #f7f7f7;
      }
      .container {
        margin-top: 50px;
      }
      .card {
        margin: auto;
        max-width: 600px;
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="card shadow">
        <div class="card-body">
          <h3 class="card-title text-center">Sube tu archivo CSV</h3>
          <p class="card-text text-center">El archivo será procesado y se agregará información de clustering en campos de texto.</p>
          <form method="post" enctype="multipart/form-data">
            <div class="custom-file mb-3">
              <input type="file" class="custom-file-input" name="file" id="file" accept=".csv" required>
              <label class="custom-file-label" for="file">Selecciona un archivo CSV</label>
            </div>
            <button type="submit" class="btn btn-primary btn-block">Procesar y Descargar</button>
          </form>
        </div>
      </div>
    </div>
    <!-- jQuery y Bootstrap JS -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>
    <script>
      // Mostrar el nombre del archivo seleccionado
      $(".custom-file-input").on("change", function() {
          var fileName = $(this).val().split("\\\\").pop();
          $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
      });
    </script>
  </body>
</html>
'''

def add_text_clusters(df, col, max_clusters=10, min_unique=10):
    """
    Si la columna 'col' tiene suficientes valores únicos, aplica TF-IDF y KMeans para agrupar los textos.
    Se agrega una nueva columna con el sufijo '_cluster' que contiene la etiqueta del cluster.
    """
    unique_values = df[col].dropna().unique()
    if len(unique_values) < min_unique:
        df[col + "_cluster"] = "n/a"
        return df

    texts = df[col].astype(str).tolist()
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(texts)
    n_clusters = min(max_clusters, len(unique_values))
    km = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = km.fit_predict(tfidf_matrix)
    df[col + "_cluster"] = clusters
    return df

def clean_csv_data(file_stream):
    # Leer el CSV
    df = pd.read_csv(file_stream)
    
    # Eliminar duplicados
    df = df.drop_duplicates()
    
    # Procesar cada columna
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col].fillna(df[col].median(), inplace=True)
        else:
            if df[col].mode().empty:
                df[col].fillna("", inplace=True)
            else:
                df[col].fillna(df[col].mode()[0], inplace=True)
            df[col] = df[col].str.strip().str.lower()
            df = add_text_clusters(df, col)
    
    # Detección de outliers en columnas numéricas
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
        
        df_clean = clean_csv_data(file)
        output = BytesIO()
        df_clean.to_csv(output, index=False)
        output.seek(0)
        
        return send_file(
            output,
            as_attachment=True,
            download_name="datos_enriquecidos.csv",
            mimetype="text/csv"
        )
    
    return render_template_string(HTML_TEMPLATE)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
