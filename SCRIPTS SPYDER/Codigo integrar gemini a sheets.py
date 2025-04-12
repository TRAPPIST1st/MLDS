# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 13:22:51 2025

@author: TRAPPIST
"""

## Función que llama a la API de Gemini para analizar el sentimiento y generar un resumen
function clasificarSentimientoYResumen(comentario) {
  var apiKey = "AIzaSyBGTTlqQxS-Ept_SEkhor1LUTnbLsbduTg"; // Reemplaza con tu API Key
  var endpoint = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=AIzaSyBGTTlqQxS-Ept_SEkhor1LUTnbLsbduTg";
  
  // Construimos el prompt que le pediremos a la IA
  var prompt = "Eres un sistema de análisis de sentimiento y resumen de texto. " +
               "Analiza el siguiente texto, determina si su sentimiento es 'Positivo', 'Negativo' o 'Neutro', " +
               "y luego escribe un resumen breve. " +
               "Devuelve el resultado en formato JSON, con las llaves 'sentiment' y 'summary' únicamente.\n\n" +
               "Texto: \"" + comentario + "\"";
  
  // Estructura del payload según lo que espera la API
  var payload = {
    "contents": [{
      "parts": [{"text": prompt}]
    }]
  };
  
  var options = {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload)
  };
  
  try {
    var response = UrlFetchApp.fetch(endpoint, options);
    var result = JSON.parse(response.getContentText());
    Logger.log("Respuesta de la API: " + JSON.stringify(result));
    
    // Validamos que se haya recibido al menos una respuesta
    if (result && result.candidates && result.candidates.length > 0) {
      var content = result.candidates[0].content;
      // Accedemos al texto generado dentro de "parts"
      var rawText = content.parts[0].text;
      Logger.log("Texto generado por la IA: " + rawText);
      
      // Limpiamos la respuesta: quitamos los backticks y la etiqueta ```json si están presentes
      var cleanedText = rawText.replace(/```json\s*/i, "").replace(/```/g, "").trim();
      
      try {
        // Intentamos parsear el JSON generado
        var jsonResultado = JSON.parse(cleanedText);
        var sentimiento = jsonResultado.sentiment || "Desconocido";
        var resumen = jsonResultado.summary || "No disponible";
        return {sentimiento: sentimiento, resumen: resumen};
      } catch (e) {
        Logger.log("Error al parsear el JSON de la IA: " + e);
        return {sentimiento: "Error", resumen: "No se pudo generar el resumen (JSON inválido)"};
      }
    }
    
    // En caso de que no se reciba una respuesta válida
    return {sentimiento: "Error", resumen: "No se recibió respuesta válida"};
    
  } catch (error) {
    Logger.log("Error al llamar la API: " + error);
    return {sentimiento: "Error", resumen: "No se pudo conectar con la API"};
  }
}

// Función para recorrer los registros de la hoja y actualizar la columna de sentimiento y resumen
function procesarFeedbacks() {
  // Abre la hoja "FeedbackAlegra". Cambia el nombre si es necesario.
  var hoja = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("feedback");
  if (!hoja) {
    Logger.log("No se encontró la hoja 'FeedbackAlegra'. Verifica el nombre.");
    return;
  }
  
  // Obtiene todos los datos; se asume que la primera fila son encabezados
  var datos = hoja.getDataRange().getValues();
  
  // Itera sobre las filas (comenzando desde la segunda, índice 1)
  for (var i = 1; i < datos.length; i++) {
    var fila = datos[i];
    var comentario = fila[2];           // Columna C (índice 2)
    var categoriaSentimiento = fila[4]; // Columna E (índice 4)
    var resumenIA = fila[5];            // Columna F (índice 5)
    
    // Si ya existe un valor en la columna de sentimiento, se salta la fila
    if (categoriaSentimiento && categoriaSentimiento !== "") continue;
    
    // Llama a la función para obtener sentimiento y resumen
    var resultado = clasificarSentimientoYResumen(comentario);
    
    // Actualiza la hoja: columna E para el sentimiento y F para el resumen
    hoja.getRange(i + 1, 5).setValue(resultado.sentimiento);
    hoja.getRange(i + 1, 6).setValue(resultado.resumen);
    
    // Pausa de 1 segundo para evitar exceder los límites de la API
    Utilities.sleep(1000);
  }
}
