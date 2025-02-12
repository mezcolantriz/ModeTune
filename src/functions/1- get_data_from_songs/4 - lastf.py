import pandas as pd
import requests
import os
from dotenv import load_dotenv
import time

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv('LASTFM_API_KEY')  # Clave de API desde el archivo .env
BASE_URL = 'http://ws.audioscrobbler.com/2.0/'

# Ruta de los archivos
input_file = r'C:\Users\solan\Downloads\get_data_from_songs\data\last2.csv'
output_file = r'C:\Users\solan\Downloads\get_data_from_songs\data\last_spoty2.csv'
error_log_file = r'C:\Users\solan\Downloads\get_data_from_songs\data\raw\last_spoty2_error.txt'

# Cargar datos existentes si ya se ha procesado parcialmente
if os.path.exists(output_file):
    processed_df = pd.read_csv(output_file)
    processed_ids = set(processed_df.index)
else:
    processed_df = pd.DataFrame()
    processed_ids = set()

# Cargar el dataset original
df = pd.read_csv(input_file)

# Función para registrar errores
def log_error(message):
    with open(error_log_file, 'a') as f:
        f.write(message + '\n')

# Función para obtener géneros desde Last.fm
def get_genres(artist):
    params = {
        'method': 'artist.getinfo',
        'artist': artist,
        'api_key': API_KEY,
        'format': 'json'
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
    return 'Unknown'

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
processed_count = 0
start_time = time.time()

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

    # Guardar cada 1000 registros procesados
    if processed_count % 1000 == 0:
        processed_df.to_csv(output_file, index=False)
        elapsed_time = time.time() - start_time
        print(f"Procesados {processed_count} registros en {elapsed_time:.2f} segundos.")

# Guardar los datos finales
processed_df.to_csv(output_file, index=False)
print(f"Procesamiento completo. Archivo guardado en {output_file}")
