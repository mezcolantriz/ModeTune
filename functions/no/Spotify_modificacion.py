import pandas as pd
import requests
import os
import time
from tqdm import tqdm
from dotenv import load_dotenv
import itertools

# 📌 Cargar variables de entorno desde .env
load_dotenv()

# 📌 Lista de credenciales de Spotify (4 usuarios para evitar bloqueos)
SPOTIFY_CREDENTIALS = [
    {
        "client_id": os.getenv("SPOTIFY_CLIENT_ID_1"),
        "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET_1"),
    },
    {
        "client_id": os.getenv("SPOTIFY_CLIENT_ID_2"),
        "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET_2"),
    },
    {
        "client_id": os.getenv("SPOTIFY_CLIENT_ID_3"),
        "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET_3"),
    },
    {
        "client_id": os.getenv("SPOTIFY_CLIENT_ID_4"),
        "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET_4"),
    },
]

# 📌 Alternar credenciales cada 40,000 filas
credential_cycle = itertools.cycle(SPOTIFY_CREDENTIALS)
current_credentials = next(credential_cycle)

# 📌 Rutas de archivos
input_file = r"C:\Users\solan\Downloads\get_data_from_songs\src\dataset_b_nulos.csv"
output_file = r"C:\Users\solan\Downloads\get_data_from_songs\data\src\dataset_b_spoty.csv"
temp_file = r"C:\Users\solan\Downloads\get_data_from_songs\data\tempb_spotify.csv"

# 📌 Columnas que queremos actualizar en Spotify
spotify_columns = ["spotify_url", "album_name", "album_release_date", "duration_ms", "popularity"]

# 📌 Función para obtener token de Spotify
def get_spotify_token():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": current_credentials["client_id"],
        "client_secret": current_credentials["client_secret"],
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

# 📌 Función para buscar una canción en Spotify
def search_spotify(artist, song, token):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": f"artist:{artist} track:{song}", "type": "track", "limit": 1}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        results = response.json()
        if results["tracks"]["items"]:
            track = results["tracks"]["items"][0]
            return {
                "spotify_url": track["external_urls"]["spotify"],
                "album_name": track["album"]["name"],
                "album_release_date": track["album"]["release_date"],
                "duration_ms": track["duration_ms"],
                "popularity": track["popularity"],
            }
    return {col: None for col in spotify_columns}

# 📌 Cargar dataset y restaurar progreso si hay un archivo temporal
def load_dataset():
    print("🔄 Cargando dataset...")
    df = pd.read_csv(input_file, encoding="utf-8", low_memory=False)

    # 📌 Asegurar que las columnas de Spotify existen
    for col in spotify_columns:
        if col not in df.columns:
            df[col] = None

    # 📌 Restaurar progreso si existe un archivo temporal
    if os.path.exists(temp_file):
        print("🔄 Recuperando progreso desde archivo temporal...")
        df_temp = pd.read_csv(temp_file, encoding="utf-8", low_memory=False)
        df.update(df_temp)
        print("✅ Progreso recuperado.")

    return df

# 📌 Función principal para actualizar dataset con Spotify
def update_spotify_data():
    global current_credentials
    df = load_dataset()
    
    # 📌 Vaciar solo las columnas de Spotify en la copia
    df[spotify_columns] = None

    # 📌 Filtrar filas sin `spotify_url`
    missing_spotify_indices = df.index.tolist()
    print(f"🎯 Canciones pendientes de buscar en Spotify: {len(missing_spotify_indices)}")

    if not missing_spotify_indices:
        print("✅ No hay filas pendientes. Nada que procesar.")
        return

    # 📌 Obtener token de Spotify
    spotify_token = get_spotify_token()

    for i, idx in enumerate(tqdm(missing_spotify_indices, desc="🔍 Buscando en Spotify", unit=" canción")):
        # 📌 Si se alcanzan 40,000 peticiones, cambiar de credenciales
        if (i + 1) % 40000 == 0:
            current_credentials = next(credential_cycle)
            spotify_token = get_spotify_token()
            print(f"🔄 Cambio de credenciales para evitar bloqueos. Nuevo usuario activado.")

        # 📌 Obtener información de Spotify
        details = search_spotify(df.at[idx, "artist_name"], df.at[idx, "song_name"], spotify_token)
        for col in spotify_columns:
            df.at[idx, col] = details[col]

        # 📌 Guardar progreso cada 1000 canciones procesadas
        if (i + 1) % 1000 == 0:
            df.to_csv(temp_file, index=False, encoding="utf-8")
            print(f"💾 Progreso guardado en {temp_file} ({i + 1} canciones procesadas).")

        # 📌 Pausar cada 5000 peticiones para evitar bloqueos
        if (i + 1) % 5000 == 0:
            print(f"⏸️ Pausa breve tras {i + 1} peticiones para evitar bloqueos de API...")
            time.sleep(10)

    # 📌 Guardar archivo final
    df.to_csv(output_file, index=False, encoding="utf-8")
    print(f"✅ Archivo final guardado en {output_file}")

    # 📌 Eliminar archivo temporal después de completar la detección
    if os.path.exists(temp_file):
        os.remove(temp_file)
        print("🗑️ Archivo temporal eliminado.")

# 📌 Ejecutar el script
if __name__ == "__main__":
    update_spotify_data()
