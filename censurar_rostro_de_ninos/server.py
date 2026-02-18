import http.server
import socketserver
import os
import json
import base64
import re

PORT = 8000
# Ruta absoluta donde quieres guardar las fotos
SAVE_DIR = r"C:\Users\maoaz\OneDrive\Documentos\MAOAZA-projects\reconocimiento-facial\censurar_rostro_de_ninos\fotos_censuradas"
CREDENTIALS_FILE = r"C:\Users\maoaz\OneDrive\Documentos\MAOAZA-projects\reconocimiento-facial\censurar_rostro_de_ninos\credentials.json"
USERS_FILE = r"C:\Users\maoaz\OneDrive\Documentos\MAOAZA-projects\reconocimiento-facial\censurar_rostro_de_ninos\users.json"

# Crear la carpeta si no existe
if not os.path.exists(SAVE_DIR):
    try:
        os.makedirs(SAVE_DIR)
        print(f"Carpeta creada: {SAVE_DIR}")
    except OSError as e:
        print(f"Error creando carpeta: {e}")

# Crear archivo de credenciales si no existe
if not os.path.exists(CREDENTIALS_FILE):
    with open(CREDENTIALS_FILE, 'w') as f:
        json.dump({}, f)
    print(f"Archivo de credenciales creado: {CREDENTIALS_FILE}")

# Crear archivo de usuarios (contraseñas) si no existe
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f:
        json.dump({}, f)
    print(f"Archivo de usuarios creado: {USERS_FILE}")

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

        elif self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                username = data.get('username')
                password = data.get('password')

                with open(USERS_FILE, 'r') as f:
                    users_db = json.load(f)

                if username in users_db and users_db[username] == password:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    # Devolvemos el username para que el cliente lo guarde
                    self.wfile.write(json.dumps({
                        'status': 'success', 
                        'token': 'token_seguro_123',
                        'username': data.get('username')
                    }).encode('utf-8'))
                else:
                    self.send_response(401)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'status': 'error', 'message': 'Credenciales incorrectas'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                print(f"Error en login: {e}")

        elif self.path == '/register-start':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            username = data['username']

            # SEGURIDAD: Verificar si el usuario ya existe para evitar que otros
            # registren sus huellas en cuentas ajenas.
            with open(USERS_FILE, 'r') as f:
                existing_users = json.load(f)
            
            if username in existing_users:
                self.send_error(409, "El usuario ya existe. No se pueden registrar mas dispositivos publicamente.")
                return

            challenge = base64.b64encode(os.urandom(32)).decode('utf-8')
            user_id = base64.b64encode(username.encode('utf-8')).decode('utf-8')

            options = {
                "challenge": challenge,
                "rp": {"name": "Sistema Facial MAOAZA"},
                "user": {
                    "id": user_id,
                    "name": username,
                    "displayName": username
                },
                "pubKeyCredParams": [{"alg": -7, "type": "public-key"}],
                "authenticatorSelection": {
                    "authenticatorAttachment": "platform",
                    "userVerification": "required"
                },
                "timeout": 60000,
                "attestation": "direct"
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(options).encode('utf-8'))

        elif self.path == '/register-finish':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            username = data['username']
            password = data['password']
            cred = data['cred']

            # En un sistema real, aquí se validaría la credencial antes de guardarla.
            # Por simplicidad, la guardamos directamente.
            with open(CREDENTIALS_FILE, 'r+') as f:
                all_creds = json.load(f)
                if username not in all_creds:
                    all_creds[username] = []
                all_creds[username].append(cred)
                f.seek(0)
                json.dump(all_creds, f, indent=4)
            
            # Guardar la contraseña en users.json
            with open(USERS_FILE, 'r+') as f:
                users = json.load(f)
                users[username] = password
                f.seek(0)
                json.dump(users, f, indent=4)
                f.truncate()

            self.send_response(200)
            self.end_headers()

        elif self.path == '/auth-start':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            username = data['username']

            with open(CREDENTIALS_FILE, 'r') as f:
                all_creds = json.load(f)
            
            if username not in all_creds or not all_creds[username]:
                self.send_error(404, "Usuario no tiene credenciales registradas")
                return

            challenge = base64.b64encode(os.urandom(32)).decode('utf-8')
            options = {
                "challenge": challenge,
                "allowCredentials": [{"type": "public-key", "id": cred['id']} for cred in all_creds[username]],
                "userVerification": "required",
                "timeout": 60000
            }
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(options).encode('utf-8'))

        elif self.path == '/auth-finish':
            # En un sistema real, aquí se haría la validación criptográfica de la firma.
            # Para este demo, simplemente aceptamos que si el navegador lo envía, es correcto.
            self.send_response(200)
            self.end_headers()

        else:
            self.send_error(404)

print(f"Servidor especial corriendo en http://localhost:{PORT}")
print(f"Las fotos se guardarán en: {SAVE_DIR}")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
