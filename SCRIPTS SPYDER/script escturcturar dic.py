# Diccionario de corrección de direcciones
correction_dict = {
    "APARTAMENTO": [
        "AP", "APARRTAMENTO", "APARTAMENTO0", "APARTAMENTOS", "APARTAMETO", "APARTARTAMENTO", "APTO"
    ],
    "ALAMEDA": [
        "AL", "ALAMEDA"
    ],
    # Añade más entradas aquí siguiendo el mismo formato
    "ALAMOS": [
        "ALAMOS"
    ],
    "ALIANZA": [
        "ALIANZA"
    ],
    "AQUABLANCA": [
        "AGUA AGUABLANCA", "AGUABLANCA"
    ],
    # Continúa para otras direcciones y sus variantes
}

#IMPLEMENTAR LA CORRECCIÓN

def correct_address(address, correction_dict):
    for correct_form, variants in correction_dict.items():
        if address in variants:
            return correct_form
    return address  # Si no hay coincidencia, retorna la dirección original

# Ejemplo de uso
address_list = [
    "AP", "APARRTAMENTO", "AL", "AGUA AGUABLANCA", "ALAMOS", "ALIANZA"
]

corrected_list = [correct_address(addr, correction_dict) for addr in address_list]
print(corrected_list)
