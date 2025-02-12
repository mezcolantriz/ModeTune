import pandas as pd
import requests
from tqdm import tqdm
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Rutas de los archivos
file_path = r"C:\Users\solan\Downloads\get_data_from_songs\src\dataset_b_nulos.csv"
output_path = r"C:\Users\solan\Downloads\get_data_from_songs\src\dataset_b_spoti.csv"

# Cargar el archivo original
df = pd.read_csv(file_path)

# Crear un DataFrame para almacenar resultados
df_result = df.copy()

# Columnas que queremos obtener del dataset
additional_columns = ['spotify_url', 'album_name', 'album_release_date', 'duration_ms', 'popularity']

# Asegurar que las columnas adicionales existen en el DataFrame de resultados
for col in additional_columns:
    if col not in df_result.columns:
        df_result[col] = None

# Obtener token de autenticación
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# Realizar una búsqueda en Spotify
def search_spotify(artist, song, token):
    url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "q": f"artist:{artist} track:{song}",
        "type": "track",
        "limit": 1
    }
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json()
        if results["tracks"]["items"]:
            track = results["tracks"]["items"][0]
            return {
                'spotify_url': track['external_urls']['spotify'],
                'album_name': track['album']['name'],
                'album_release_date': track['album']['release_date'],
                'duration_ms': track['duration_ms'],
                'popularity': track['popularity']
            }
    return {col: None for col in additional_columns}

# Obtener el token de Spotify
spotify_token = get_spotify_token()

# Aplicar la función a cada fila y actualizar el DataFrame resultante
for index, row in tqdm(df_result.iterrows(), total=len(df_result), desc="Procesando canciones"):
    details = search_spotify(row['artist_name'], row['song_name'], spotify_token)
    for col in additional_columns:
        df_result.at[index, col] = details[col]

# Guardar el resultado en un nuevo archivo
df_result.to_csv(output_path, index=False)

# Mostrar mensaje de éxito
print(f"Archivo enriquecido guardado en: {output_path}")
