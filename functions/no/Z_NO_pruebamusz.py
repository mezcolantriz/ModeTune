import pandas as pd
import requests
import time
import os

# Rutas de los archivos
data_path = r"C:\Users\solan\Downloads\get_data_from_songs\data\raw\data_to_processbea4.csv"
output_path_found = r"C:\Users\solan\Downloads\get_data_from_songs\data\raw\4_nuevos_ids_encontrados.csv"
output_path_not_found = r"C:\Users\solan\Downloads\get_data_from_songs\data\raw\4_ids_no_encontrados.csv"

# Cargar el dataset original
df = pd.read_csv(data_path)

# Verificar si las columnas necesarias existen
required_columns = ['artist_name', 'song_name']
if not all(col in df.columns for col in required_columns):
    raise ValueError(f"El archivo debe contener las columnas: {required_columns}")

# Agregar la columna 'recording_id' si no existe
if 'recording_id' not in df.columns:
    df['recording_id'] = None

# Función para normalizar nombres
def normalize_name(name):
    if "," in name:
        parts = [part.strip() for part in name.split(",")]
        name = " ".join(reversed(parts))
    return "".join(e for e in name if e.isalnum() or e.isspace()).strip()

# Función para buscar información en MusicBrainz
def search_musicbrainz(artist, title):
    base_url = "https://musicbrainz.org/ws/2/recording/"
    headers = {
        'User-Agent': 'mezcoind (solana93@gmail.com)'
    }
    query = f'artist:"{normalize_name(artist)}" AND recording:"{normalize_name(title)}"'
    params = {'query': query, 'fmt': 'json'}
    try:
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        if data.get('recordings'):
            recording = data['recordings'][0]
            return {'recording_id': recording.get('id')}
    except Exception:
        return None

# Iterar sobre las canciones que no han sido procesadas
total_songs = len(df)
print(f"Comenzando el procesamiento de {total_songs} canciones...")

for idx, row in df.iterrows():
    artist = row['artist_name']
    title = row['song_name']

    # Saltar si ya tiene un ID
    if pd.notna(row['recording_id']):
        continue

    print(f"Procesando fila {idx + 1}/{total_songs}: {artist} - {title}...")

    result = search_musicbrainz(artist, title)
    if result:
        df.at[idx, 'recording_id'] = result['recording_id']

    # Guardar progreso cada 100 filas
    if (idx + 1) % 100 == 0:
        print(f"Progreso: {idx + 1} de {total_songs} filas procesadas.")
        df.to_csv(data_path, index=False)

    # Pausa para evitar ser bloqueado por la API
    time.sleep(1)

# Separar en encontrados y no encontrados
found_ids = df[df['recording_id'].notna()]
not_found_ids = df[df['recording_id'].isna()]

# Guardar los resultados finales
found_ids.to_csv(output_path_found, index=False)
not_found_ids.to_csv(output_path_not_found, index=False)

print(f"Proceso completado. Resultados:")
print(f"- IDs encontrados guardados en: {output_path_found}")
print(f"- IDs no encontrados guardados en: {output_path_not_found}")
