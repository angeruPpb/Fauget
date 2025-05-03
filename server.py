from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import mysql.connector
import os
import mimetypes 
from urllib.parse import urlparse, parse_qs

# Configuración de XAMPP (usuario root sin contraseña por defecto)
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'proyecto'
}

def agregar_categoria(data):
    nombre = data['nombre']
    categoria_padre = data['categoria_padre']

    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute("INSERT INTO TablaCategorias (nombre, categoria_padre) VALUES (%s, %s)", (nombre, categoria_padre))
        conexion.commit()
        return True
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def eliminar_categoria(data):
    nombre = data.get('nombre')
    categoria_padre = data.get('categoria_padre')

    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor()

        # Verificar si la categoría existe con el nombre y la categoría padre
        cursor.execute("SELECT COUNT(*) FROM TablaCategorias WHERE nombre = %s AND categoria_padre = %s", (nombre, categoria_padre))
        existe = cursor.fetchone()[0] > 0

        if not existe:
            print(f"La categoría '{nombre}' con padre '{categoria_padre}' no existe.")
            return False

        # Actualizar los contenidos asociados a la categoría eliminada
        #cursor.execute(
        #    "UPDATE TablaContenidos SET categoria = %s WHERE categoria = %s",
        #    (categoria_padre, nombre)
        #)

        # Eliminar la categoría
        cursor.execute("DELETE FROM TablaCategorias WHERE nombre = %s AND categoria_padre = %s", (nombre, categoria_padre))
        conexion.commit()

        print(f"Categoría '{nombre}' con padre '{categoria_padre}' eliminada correctamente. Contenidos reasignados a la categoría padre '{categoria_padre}'.")
        return True
    except mysql.connector.Error as err:
        print(f"Error al eliminar la categoría: {err}")
        return False
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def editar_categoria(data):
    nombre_actual = data.get('nombre_actual')
    nuevo_nombre = data.get('nuevo_nombre')

    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor()

        # Actualizar el nombre de la categoría
        cursor.execute("UPDATE TablaCategorias SET nombre = %s WHERE nombre = %s", (nuevo_nombre, nombre_actual))
        conexion.commit()

        print(f"Categoría '{nombre_actual}' actualizada a '{nuevo_nombre}'.")
        return True
    except mysql.connector.Error as err:
        print(f"Error al editar la categoría: {err}")
        return False
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def verificar_categoria(nombre, padre):
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM TablaCategorias WHERE nombre = %s AND categoria_padre = %s", (nombre, padre))
        existe = cursor.fetchone()[0] > 0

        # Imprimir en la consola si la categoría existe o no
        if existe:
            print(f"La categoría '{nombre}' con padre '{padre}' ya existe.")
        else:
            print(f"La categoría '{nombre}' con padre '{padre}' no existe.")

        return existe
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return False
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

class Manejador(BaseHTTPRequestHandler):
    # Configuración de rutas
    RUTAS = {
        '/': 'login.html',
        '/AdminPaginaPrincipal': 'AdminPaginaPrincipal.html',
        '/AdminGestorContenido': 'AdminGestorContenido.html',
        '/AdminGestorPromociones': 'AdminGestorPromociones.html',
        '/AdminGestorCategorias': 'AdminGestorCategorias.html',
        '/logout': None
    }
    
    # Plantilla base común
    BASE_HTML = None

    def do_GET(self):
        path = self.path.split('?')[0]  # Ignorar parámetros en la URL

        # Manejar la ruta de la página principal del administrador
        if path == '/AdminPaginaPrincipal':
            self.serve_page('AdminPaginaPrincipal.html')
            return

        # Manejar la ruta de gestionar contenido
        if path == '/AdminGestorContenido':
            self.serve_page('AdminGestorContenido.html')
            return

        # Manejar la ruta de gestionar categorías
        if path == '/AdminGestorCategorias':
            self.serve_page('AdminGestorCategorias.html')
            return
        
        if self.path.startswith('/verificarCategoria'):
            query = parse_qs(urlparse(self.path).query)
            nombre = query.get('nombre', [None])[0]
            padre = query.get('padre', [None])[0]

            if nombre and padre:
                existe = verificar_categoria(nombre, padre)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'existe': existe}).encode('utf-8'))
                return  # Detener el flujo después de enviar la respuesta
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': "Faltan los parámetros 'nombre' o 'padre'"}).encode('utf-8'))
                return  # Detener el flujo después de enviar la respuesta

        # Manejar la ruta de gestionar promociones
        if path == '/AdminGestorPromociones':
            self.serve_page('AdminGestorPromociones.html')
            return

        # Manejar la ruta de cargar saldo
        if path == '/CargarSaldo':
            self.serve_page('CargarSaldo.html')
            return

        # Manejar la ruta de logout
        if path == '/logout':
            self.redirect('/')
            return

        # Si la ruta no coincide con ninguna, devolver un error 404
        self.send_error(404, "Página no encontrada")
    
    def serve_admin_page(self, path):
        try:
            # Cargar la plantilla base
            with open(os.path.join('templates', 'AdminBase.html'), 'r', encoding='utf-8') as f:
                base_html = f.read()

            # Cargar la plantilla específica según la ruta
            if path == '/AdminPaginaPrincipal':
                with open(os.path.join('templates', 'AdminPaginaPrincipal.html'), 'r', encoding='utf-8') as f:
                    content_html = f.read()
            else:
                content_html = "<h1>Página no encontrada</h1>"

            # Reemplazar el bloque `{% block content %}` en la plantilla base
            full_html = base_html.replace("{% block content %}{%}", content_html)

            # Enviar la respuesta al cliente
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(full_html.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "Archivo no encontrado")
    
    def serve_static(self, filename):
        try:
            file_path = os.path.join('templates', filename)
            if not os.path.isfile(file_path):
                self.send_error(404)
                return

            mime_type, _ = mimetypes.guess_type(file_path)
            with open(file_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-type', mime_type or 'application/octet-stream')
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f'Error interno: {e}')

    def serve_static_file(self, path):
        try:
            # Construir la ruta completa del archivo estático
            file_path = os.path.normpath(os.path.join('static', path.lstrip('/static/')))
            
            # Verificar si el archivo existe
            if not os.path.isfile(file_path):
                print(f"Archivo no encontrado: {file_path}")  # Debug
                self.send_error(404)
                return

            # Determinar el tipo MIME del archivo
            mime_type, _ = mimetypes.guess_type(file_path)
            if not mime_type:
                if file_path.endswith('.css'):
                    mime_type = 'text/css'
                elif file_path.endswith('.js'):
                    mime_type = 'application/javascript'
            
            # Leer y servir el archivo
            with open(file_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-type', mime_type)
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            print(f"Error al servir archivo estático: {str(e)}")  # Debug
            self.send_error(500, f'Error interno: {str(e)}')
        print(f"Sirviendo archivo estático: {file_path}")
    
    def serve_page(self, template_name):
        """Sirve una página HTML desde la carpeta de plantillas."""
        try:
            # Cargar la plantilla HTML
            with open(os.path.join('templates', template_name), 'r', encoding='utf-8') as f:
                html = f.read()

            # Enviar la respuesta al cliente
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "Archivo no encontrado")

    def redirect(self, location):
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()

    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = dict(x.split('=') for x in post_data.split('&'))
            
            username = params.get('username')
            password = params.get('password')
            
            try:
                conexion = mysql.connector.connect(**DB_CONFIG)
                cursor = conexion.cursor(dictionary=True)
                cursor.execute("SELECT * FROM TablaUsuarios WHERE username_ = %s AND password_ = %s", (username, password))
                usuario = cursor.fetchone()
                
                if usuario:
                    # Redirigir al administrador
                    self.redirect('/AdminPaginaPrincipal')
                else:
                    # Credenciales incorrectas
                    self.send_response(401)
                    self.end_headers()
                    self.wfile.write(b"Credenciales incorrectas")
            except mysql.connector.Error as err:
                self.send_error(500, f"Error de MySQL: {err}")
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'conexion' in locals(): conexion.close()
        
        if self.path == '/agregarCategoria':
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))
            if agregar_categoria(post_data):
                self.send_response(200)
            else:
                self.send_error(500)
            self.end_headers()

        elif self.path == '/eliminarCategoria':
            content_length = int(self.headers['Content-Length'])
            post_data = json.loads(self.rfile.read(content_length))

            nombre = post_data.get('nombre')
            categoria_padre = post_data.get('categoria_padre')

            if not nombre or not categoria_padre:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Faltan parámetros'}).encode('utf-8'))
                return

            try:
                resultado = eliminar_categoria({'nombre': nombre, 'categoria_padre': categoria_padre})
                if resultado:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'mensaje': 'Categoría eliminada correctamente'}).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Error al eliminar la categoría'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
    
        elif self.path == '/editarCategoria':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            nombre_actual = data.get('nombre_actual')
            nuevo_nombre = data.get('nuevo_nombre')

            if not nombre_actual or not nuevo_nombre:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Faltan parámetros'}).encode('utf-8'))
                return

            try:
                resultado = editar_categoria({'nombre_actual': nombre_actual, 'nuevo_nombre': nuevo_nombre})
                if resultado:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'mensaje': 'Categoría editada correctamente'}).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Error al editar la categoría'}).encode('utf-8'))
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))

def ejecutar_servidor(puerto=8000):
    servidor = HTTPServer(('', puerto), Manejador)
    print(f'Servidor en http://localhost:{puerto}')
    servidor.serve_forever()

if __name__ == '__main__':
    ejecutar_servidor()