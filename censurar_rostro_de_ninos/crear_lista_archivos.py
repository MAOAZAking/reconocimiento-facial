import os
import json

# Define el directorio donde están las imágenes.
# Hacemos la ruta relativa al script para que sea más robusto.
script_dir = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(script_dir, 'fotos_limpias')
output_file = os.path.join(script_dir, 'fotos_limpias', 'file_list.json')

# Extensiones de archivo de imagen que queremos incluir
valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']

try:
    # Listar solo los archivos que tengan una extensión de imagen válida
    files = [f for f in os.listdir(image_dir) if os.path.splitext(f)[1].lower() in valid_extensions]
    
    # Guardar la lista en el archivo JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(files, f, indent=4)
        
    print(f"¡Éxito! Se creó el archivo '{output_file}' con {len(files)} imágenes.")
    
except FileNotFoundError:
    print(f"Error: No se encontró el directorio '{image_dir}'. Asegúrate de que la carpeta 'fotos_limpias' exista en el mismo directorio que este script.")