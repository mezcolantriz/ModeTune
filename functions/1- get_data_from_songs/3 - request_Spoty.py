
"""

🎯 **Objetivo del Script**:

Enriquecer los datos de las canciones obtenidas de MusicBrainz con información adicional proporcionada por la API de Spotify, 
como la URL de Spotify, nombre del álbum, fecha de lanzamiento del álbum, duración de la canción y popularidad.
Se ha utilizado tanto para nuevos datos como para trabajar los que no se habían o habían sido mal enriquecidos. 
Dejamos esta versión pero se han hecho distintas copias adecuándose al objetivo. Este script realiza las siguientes acciones:

1. 📚 **Importación de Librerías**:
    - Importamos las librerías necesarias para la manipulación de datos (`pandas`), realizar solicitudes HTTP (`requests`), mostrar una barra de progreso (`tqdm`), y cargar variables de entorno (`dotenv`).

2. 🔑 **Cargar Variables de Entorno**:
    - Utilizamos `dotenv` para cargar las credenciales de la API de Spotify desde un archivo `.env`.

3. 🗂️ **Definir Rutas de Archivos**:
    - Especificamos las rutas de los archivos de entrada y salida. El archivo de entrada contiene los datos extraídos previamente de MusicBrainz.

4. 📥 **Cargar el Archivo Original**:
    - Cargamos el archivo CSV original que contiene los datos de las canciones.

5. 📝 **Preparar el DataFrame para Resultados**:
    - Creamos un DataFrame de resultados copiando el original y añadimos columnas adicionales para almacenar la información obtenida de Spotify.

6. 🔐 **Obtener Token de Autenticación**:
    - Definimos una función `get_spotify_token` para obtener un token de autenticación de la API de Spotify utilizando las credenciales cargadas.

7. 🔍 **Buscar Información en Spotify**:
    - Definimos una función `search_spotify` que realiza una búsqueda en la API de Spotify para obtener información adicional sobre cada canción (URL de Spotify, nombre del álbum, fecha de lanzamiento del álbum, duración de la canción, popularidad).

8. 🔄 **Aplicar la Función a Cada Fila**:
    - Iteramos sobre cada fila del DataFrame original, utilizamos la función `search_spotify` para obtener información adicional y actualizamos el DataFrame de resultados.

9. 💾 **Guardar el Resultado**:
    - Guardamos el DataFrame de resultados en un nuevo archivo CSV.

10. 🎉 **Mostrar Mensaje de Éxito**:
     - Imprimimos un mensaje indicando que el archivo enriquecido ha sido guardado exitosamente.

Este script permite enriquecer los datos de las canciones obtenidas de MusicBrainz con información adicional proporcionada por la API de Spotify.
"""

import pandas as pd     # manipulación de datos
import requests     # solicitudes HTTP
from tqdm import tqdm # barra de progreso
from dotenv import load_dotenv  # cargar variables de entorno
import os # rutas de archivos

# Cargar variables de entorno
load_dotenv() # Cargar credenciales de Spotify desde un archivo .env
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")

# Rutas de los archivos
file_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'dataset_b_nulos.csv')
output_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src', 'dataset_b_spoti.csv')

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

# Obtener token de autenticación de Spotify
def get_spotify_token():
    
    #btiene un token de autenticación de la API de Spotify utilizando las credenciales del archivo .env.
   
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded" # tipo de contenido de la solicitud
    }
    data = {
        "grant_type": "client_credentials",     # tipo de concesión
        "client_id": SPOTIFY_CLIENT_ID, 
        "client_secret": SPOTIFY_CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data) # solicitud POST
    response.raise_for_status()     # si hay un error en la solicitud, se lanza una excepción
    return response.json()["access_token"] # devuelve el token de acceso

# Realizar una búsqueda en Spotify
def search_spotify(artist, song, token):
    """
    Realiza una búsqueda en la API de Spotify para obtener información adicional sobre una canción.
    
    Args:
        artist (str): Nombre del artista.
        song (str): Nombre de la canción.
        token (str): Token de autenticación de Spotify.
    
    Returns:
        dict: Información adicional de la canción obtenida de Spotify.
    """
    url = "https://api.spotify.com/v1/search"
    headers = {
        "Authorization": f"Bearer {token}" 
    }
    params = {
        "q": f"artist:{artist} track:{song}",
        "type": "track",
        "limit": 1
    }
    response = requests.get(url, headers=headers, params=params) # solicitud GET
    if response.status_code == 200: # si la solicitud es exitosa
        results = response.json() # obtener los resultados
        if results["tracks"]["items"]:      # si hay canciones encontradas
            track = results["tracks"]["items"][0] # obtener la primera canción
            return {
                'spotify_url': track['external_urls']['spotify'],   # URL de Spotify
                'album_name': track['album']['name'],   # nombre del álbum
                'album_release_date': track['album']['release_date'],   # fecha de lanzamiento del álbum
                'duration_ms': track['duration_ms'],    # duración de la canción
                'popularity': track['popularity']   # popularidad
            }
    return {col: None for col in additional_columns} # si no se encuentra la canción, devolver valores nulos

# Obtener el token de Spotify
spotify_token = get_spotify_token()

# Aplicar la función a cada fila y actualizar el DataFrame resultante
for index, row in tqdm(df_result.iterrows(), total=len(df_result), desc="Procesando canciones"):    
    details = search_spotify(row['artist_name'], row['song_name'], spotify_token)   
    for col in additional_columns:  
        df_result.at[index, col] = details[col]     # actualizar el DataFrame de resultados

# Guardar el resultado en un nuevo archivo
df_result.to_csv(output_path, index=False)

# Mostrar mensaje de éxito
print(f"Archivo enriquecido guardado en: {output_path}")

# Siguiente paso... LastFM :) 