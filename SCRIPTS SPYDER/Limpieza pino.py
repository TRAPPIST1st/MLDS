import pandas as pd 

# Cargar el conjunto de datos del archivo 
df = pd.read_csv('data.csv')

# Ver la primera fila (RÓTULOS)
print(df.head())

# Identificar valores nulos 
print('Valores nulos en cada columna:')
print(df.isnull().sum())

#Remplazar valores nulos
df = df.fillna("NN")
print(df)

# Identificar valores duplicados 
dobles = df.duplicated().sum()
print(f'Número de duplicados: {dobles}')

# Eliminar duplicados 
df = df.drop_duplicates()

# Renombrar columnas (corrige el nombre de la columna si es necesario)
df.rename(columns={'antiguo_nombre': 'nuevo'}, inplace=True)  # Asegúrate de que el nombre sea correcto

# Guardar los datos limpios en un nuevo archivo CSV
df.to_csv('datos_limpios.csv', index=False)
print('Datos limpios y guardados.')
