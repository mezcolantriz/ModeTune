"""
 Este script tiene como objetivo procesar el conjunto de datos que tenemos activo, obteniendo géneros y tags desde la API de Last.fm. 
El objetivo principal es enriquecer los datos de las canciones con información adicional que pueda ser utilizada en el 
recomendador de música basado en frases del usuario y poder filtrar con géneros y tags. 🎶

📂 El script carga un archivo CSV con los datos de canciones, consulta la API de Last.fm para obtener información, y guarda los resultados en un nuevo archivo CSV. 📊
"""

import pandas as pd 
import requests     # Solicitudes HTTP
import os   # Rutas de archivos
from dotenv import load_dotenv  # Cargar variables de entorno
import time     # Medir el tiempo de ejecución

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv('LASTFM_API_KEY')  # Clave de API desde el archivo .env
BASE_URL = 'http://ws.audioscrobbler.com/2.0/'  # URL base de la API de Last.fm

# Ruta de los archivos
input_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'last2.csv')   # Archivo de entrada
output_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'last_spoty2.csv')    # Archivo de salida
error_log_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw', 'last_spoty2_error.txt')    # Archivo de registro de errores

# Cargar datos existentes si ya se ha procesado parcialmente
if os.path.exists(output_file):     
    processed_df = pd.read_csv(output_file)     
    processed_ids = set(processed_df.index) # Conjunto de IDs procesados                  
else:
    processed_df = pd.DataFrame()   # Crear un DataFrame vacío
    processed_ids = set()   # Conjunto vacío de IDs procesados

# Cargar el dataset original
df = pd.read_csv(input_file)    

# Función para registrar errores
def log_error(message):
    with open(error_log_file, 'a') as f:    # Abrir el archivo en modo de escritura
        f.write(message + '\n')     # Escribir el mensaje de error

# Función para obtener géneros desde Last.fm utilizando estos datos que ya tenemos
def get_genres(artist):
    params = {
        'method': 'artist.getinfo',     # Método de la API
        'artist': artist,   # Nombre del artista
        'api_key': API_KEY,     # Clave de API
        'format': 'json'        # Formato de respuesta
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()     
        data = response.json()
        if 'artist' in data and 'tags' in data['artist']:
            genres = [tag['name'] for tag in data['artist']['tags']['tag']]
            return ', '.join(genres) if genres else 'Unknown'
    except Exception as e:
        error_message = f"Error al obtener géneros para el artista '{artist}': {e}"
        print(error_message)
        log_error(error_message)
    return 'Unknown'   # Si no se pueden obtener los géneros, se devuelve 'Unknown'

# Función para obtener tags desde Last.fm
def get_track_tags(artist, track):
    params = {
        'method': 'track.getinfo',
        'artist': artist,
        'track': track,
        'api_key': API_KEY,
        'format': 'json'
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if 'track' in data and 'toptags' in data['track']:
            tags = [tag['name'] for tag in data['track']['toptags']['tag']]
            return ', '.join(tags) if tags else 'Unknown'
    except Exception as e:
        error_message = f"Error al obtener tags para la canción '{track}' de '{artist}': {e}"
        print(error_message)
        log_error(error_message)
    return 'Unknown'

# Procesar filas para añadir géneros y tags
def process_row(index, row):         
    artist = row['artist_name']
    track = row['song_name']
    genres = get_genres(artist)
    tags = get_track_tags(artist, track)    
    return genres, tags     

print("Procesando el dataset...")
processed_count = 0     # Contador de registros procesados
start_time = time.time()    # Tiempo de inicio

# Iterar sobre cada fila del DataFrame
for index, row in df.iterrows():
    if index in processed_ids:
        continue

    genres, tags = process_row(index, row)
    row['genres'] = genres
    row['tags'] = tags
    processed_df = pd.concat([processed_df, pd.DataFrame([row])], ignore_index=True)
    processed_count += 1

    # Imprimir progreso de cada canción procesada
    print(f"Procesado: {row['artist_name']} - {row['song_name']}")

    # Guardar cada 1000 registros procesados para no perder los datos por el camino
    if processed_count % 1000 == 0:
        processed_df.to_csv(output_file, index=False)
        elapsed_time = time.time() - start_time
        print(f"Procesados {processed_count} registros en {elapsed_time:.2f} segundos.")

# Guardar los datos finales
processed_df.to_csv(output_file, index=False)
print(f"Procesamiento completo. Archivo guardado en {output_file}")
