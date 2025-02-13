# Introducción

"""
"Este script tiene como objetivo detectar el idioma de las letras de canciones en un archivo CSV y añadir una columna con el idioma detectado.
Esta es una alternativa primera para detectar el idioma de las canciones y luego poder filtrar y traducir aquellas que no estén en español.
El script utiliza la biblioteca `langdetect` para identificar el idioma de las letras y `pandas` para manipular el archivo CSV.
 Se configura un intervalo de guardado y una pausa para evitar sobrecargar el sistema durante el procesamiento de grandes cantidades de datos.

A continuación se presenta el código completo del script: """



import pandas as pd
from langdetect import detect, DetectorFactory
import os
import time

# Configurar aleatoriedad para reproducibilidad
DetectorFactory.seed = 0   

# Esta función coge un texto como entrada y devuelve el idioma detectado. Si hay algún error devuelve None.
def detect_language(text):
    try:
        return detect(text)
    except Exception as e:
        return None

def add_language_column(input_file, output_file, save_interval=1000, pause_interval=5000):
    """
    Detecta el idioma de las letras y añade una columna al dataset.
    :param input_file: Ruta del archivo CSV de entrada
    :param output_file: Ruta del archivo CSV de salida
    :param save_interval: Número de filas procesadas antes de guardar el archivo
    :param pause_interval: Número de filas procesadas antes de pausar brevemente
    """
    try:
        # Leer el archivo original
        df = pd.read_csv(input_file)

        # Verificar si ya existe la columna 'LANGUAGE'
        if 'language' not in df.columns:
            df['language'] = None

        # Filtrar filas sin idioma detectado
        rows_to_process = df[df['language'].isnull()]
        print(f"Filas restantes por procesar: {len(rows_to_process)}")

        if rows_to_process.empty:
            print("No hay filas para procesar.")
            return

        for index, row in rows_to_process.iterrows():
            # Detectar el idioma
            language = detect_language(row['lyrics'])
            df.at[index, 'language'] = language

            # Imprimir progreso
            if (index + 1) % 100 == 0:
                print(f"Procesadas {index + 1}/{len(rows_to_process)} filas.")

            # Guardar cada `save_interval` filas procesadas
            if (index + 1) % save_interval == 0:
                print(f"Guardando progreso en {output_file}...")
                df.to_csv(output_file, index=False)

            # Pausar cada `pause_interval` filas procesadas
            if (index + 1) % pause_interval == 0:
                print(f"Pausa breve tras procesar {index + 1} filas para evitar sobrecarga...")
                time.sleep(30)  # Pausa de 10 segundos

        # Guardar el dataset actualizado al finalizar
        print(f"Guardando archivo final en {output_file}...")
        df.to_csv(output_file, index=False)
        print("Proceso completo.")

    except FileNotFoundError:
        print(f"El archivo {input_file} no se encontró. Verifica la ruta.")
    except Exception as e:
        print(f"Se produjo un error: {e}")

if __name__ == "__main__":
    # Directorio base para los archivos
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    input_file = os.path.join(base_dir, "data", "final_idiomas_traducido.csv")
    output_file = os.path.join(base_dir, "data", "final_idiomas_tr.csv")

    # Ejecutar el procesamiento
    add_language_column(input_file, output_file, save_interval=1000, pause_interval=5000)
