# Almacenamiento de canciones procesadas
En [all_processed_songs.csv](data/processed/all_processed_songs.csv) se añaden todos los registros que ya se han procesado, para luego limpiar los nulos o NaN y guardar los datos limpios en [clean_processed_songs.csv](data/processed/clean_processed_songs.csv)


# Búsqueda de más datos basados en el recording_id
En [more_songs_with_data.csv.temp](data/raw/more_songs_with_data.csv.temp) se irán guardando los registros que se obtengan al ejecutar el código de [get-song-data.ipynb](src/get-song-data.ipynb).

MUY IMPORTANTE:
- A veces el guardado del archivo temporal falla, por lo que lo ideal es eliminarlo (o cambiar el nombre del actual si no queremos perder sus registros) antes de ejecutar la búsqueda para evitar que haya problemas al intentar sobrescribirlo.

- Del mismo modo, si la búsqueda se para, lo ideal sería almacenar los registros que ya haya procesado en un .csv y quitarlos del dataset que vayamos a procesar, así no tendrá que recorrer todos nuevamente.


# Otras funciones
En [utils.py](src/utils.py) hay varias funciones como fix_artists_names() para corregir los nombres de artistas que vienen invertidos o get_recording_id_by_song() para obtener el recording_id de una canción de MusicBrainz teniendo su song_name y artist_name. Para usarlas solo será necesario importar utils en el archivo que queramos y llamarlas del siguiente modo:

### Ejemplo de uso

Para utilizar las funciones de `utils`, puedes usar el siguiente código:

```python
import utils

utils.fix_artists_names(datasetDelQueQuieroCorregirLosArtistNames, rutaDondeSeGuardaráElCsvConLosNombresCorregidos)
utils.get_recording_id_by_song(datasetQueQuieroProcesar)
