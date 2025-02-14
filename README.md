# MoodTune

## Descripción

MoodTune es una aplicación diseñada por Miriam Jurado, Jesús Piñeiro y Beatriz Solana para mejorar tu estado de ánimo a través de la música personalizada. Utiliza algoritmos avanzados para seleccionar canciones que se adapten a tus emociones actuales teniendo en cuenta tanto las letras como las características musicales, tú eliges lo que más se adapte a ti.

## Contribución
Si deseas contribuir a MoodTune, por favor sigue estos pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva funcionalidad'`).
4. Sube tus cambios (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

Puedes ver en la memoria del proyecto (`functions\Memoria_Proyecto_Actualizado.ipynb`)
todos los pasos y scripts además de los directorios del despliegue local.


## **7. Ejecución del proyecto en tu entorno local**

1. **Clonar o hacer fork del repositorio con el backend del proyecto en tu entorno local**:
   [Repositorio de Backend](https://github.com/JCMiriam/mood_tune_back)

   - Crear y activar entorno virtual para el proyceto:
      Para Windows
      ```bash
      python -m venv venv
      venv\Scripts\activate
      ```

      Para macOS/Linux
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

   - Instalar dependencias
      ```bash
      pip install -r requirements.txt
      ```

   - Añadir variables de entorno en el .env utilizando el .env.example como referencia. Dado que estas variables serán secrets, es necesario solicitarlas a uno de los creadores del proyecto o configurarlas en una aplicación de Spotify propias

   - Incluir los modelos descargables de [este directorio](https://drive.google.com/drive/folders/1i-Mq9OqLtSa0eTa0wxmNM41MtwTsX2eK?usp=sharing) en src/models/

   - Incluir el [dataset descargable](https://drive.google.com/file/d/1oTyziRBXkNGAjplpkHzYWFI6YLh5YBKL/view?usp=sharing) en src/data/ y actualizar la ruta en DATASET_PATH del archivo dataset_loader según las necesidades del entorno

   - Ejecutar la aplicación
      ```bash
            python run.py
      ```

   - Si es necesario, actualizar o instalar dependencias faltantes

   - El servidor estará disponible en http://127.0.0.1:5000
      

2. **Clonar o hacer fork del repositorio con el frontend del proyecto en tu entorno local** Es necesario tener node instalado:
   [Repositorio de Frontend](https://github.com/JCMiriam/mood_tune_front)

   - Añadir variables de entorno en el .env utilizando el .env.example como referencia

   - Instalar dependencias
      ```bash
      npm run install
      ```

   - Ejecutar la aplicación
      ```bash
      npm run dev
      ```

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.



