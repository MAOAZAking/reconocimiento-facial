import http.server
import socketserver
import os
import json
import base64
import re

PORT = 8000
# Ruta absoluta donde quieres guardar las fotos
SAVE_DIR = r"C:\Users\maoaz\OneDrive\Documentos\MAOAZA-projects\reconocimiento-facial\censurar_rostro_de_ninos\fotos_censuradas"

# Crear la carpeta si no existe
if not os.path.exists(SAVE_DIR):
    try:
        os.makedirs(SAVE_DIR)
        print(f"Carpeta creada: {SAVE_DIR}")
    except OSError as e:
        print(f"Error creando carpeta: {e}")

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        # Manejar la subida de imágenes
        if self.path == '/save-image':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                filename = data['filename']
                image_data = data['image']
                
                # Limpiar el encabezado data:image/jpeg;base64,
                image_data = re.sub('^data:image/.+;base64,', '', image_data)
                
                # Decodificar y guardar
                binary_data = base64.b64decode(image_data)
                filepath = os.path.join(SAVE_DIR, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(binary_data)
                
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'success', 'path': filepath}).encode('utf-8'))
                print(f"Guardado: {filename}")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                print(f"Error guardando imagen: {e}")
        else:
            self.send_error(404)

print(f"Servidor especial corriendo en http://localhost:{PORT}")
print(f"Las fotos se guardarán en: {SAVE_DIR}")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
