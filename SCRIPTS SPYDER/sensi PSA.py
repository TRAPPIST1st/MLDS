# -*- coding: utf-8 -*-
"""
Created on Mon Jan 20 01:25:13 2025

@author: TRAPPIST
"""

def psa_method_calculator(base_sensitivity, iterations):
    """
    PSA Method Calculator adaptado para sensibilidades enteras con iteraciones.

    Args:
        base_sensitivity (int): Sensibilidad inicial.
        iterations (int): Número de iteraciones para ajustar la sensibilidad.

    Returns:
        list: Lista de diccionarios con las sensibilidades sugeridas en cada iteración.
    """
    if not isinstance(base_sensitivity, int):
        raise ValueError("La sensibilidad base debe ser un número entero.")
    if not isinstance(iterations, int) or iterations <= 0:
        raise ValueError("El número de iteraciones debe ser un entero positivo.")

    sensitivities_history = []
    current_base = base_sensitivity

    for i in range(iterations):
        step = 1  # Incremento fijo para sensibilidades enteras

        # Calcular sensibilidades para esta iteración
        low_sensitivity = current_base - step
        high_sensitivity = current_base + step
        lower_mid_sensitivity = current_base - 2 * step
        higher_mid_sensitivity = current_base + 2 * step

        # Crear el diccionario de resultados para esta iteración
        sensitivities = {
            "Iteration": i + 1,
            "Base Sensitivity": current_base,
            "Lower Sensitivity": max(1, low_sensitivity),  # Asegurarse de que no sea menor a 1
            "Higher Sensitivity": high_sensitivity,
            "Lower Mid Sensitivity": max(1, lower_mid_sensitivity),
            "Higher Mid Sensitivity": higher_mid_sensitivity
        }

        sensitivities_history.append(sensitivities)

        # Actualizar la base para la siguiente iteración
        # El usuario debería elegir entre Low y High, pero aquí simulamos un ajuste hacia "Higher"
        current_base = high_sensitivity  # Ajuste simulado para iterar

    return sensitivities_history

# Ejemplo de uso
base_sensitivity = 30  # Cambia esto según tu sensibilidad inicial
iterations = 7  # Número de iteraciones a realizar
result = psa_method_calculator(base_sensitivity, iterations)

print("Historial de sensibilidades sugeridas para el PSA Method:")
for entry in result:
    print(entry)
