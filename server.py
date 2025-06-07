import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import mysql.connector   
import os
import mimetypes 
import decimal
from gestorConfig import DB_CONFIG
from gestorCategoria import *
from gestorContenido import *
from gestorPromocion import *
from gestorPerfil import *
from gestorSesion import *
from urllib.parse import urlparse, parse_qs


class Manejador(BaseHTTPRequestHandler):
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

    # gestorSesion para leer la sesión y redirigir si no existe
    def get_cliente(self):
        return obtener_cliente_sesion(self.headers, self.redirect)

    def do_GET(self):
        path = self.path.split('?')[0] 

        if path == '/':
            self.serve_page('login.html')
            return
        
        if path == '/AdminPaginaPrincipal':
            self.serve_page('AdminPaginaPrincipal.html')
            return
        if path == '/ClientePaginaPrincipal':
            cliente = self.get_cliente()
            if not cliente: return
            self.serve_page('ClientePaginaPrincipal.html', cliente=cliente)
            return
        if path == '/Perfil':
            cliente = self.get_cliente()
            if not cliente: return
            self.serve_page('Perfil.html', cliente=cliente)
            return
        

        ############################
        ### GESTIONAR SESION ###
        ############################

        # ENDPOINT: Aquí este endpoint devuelve los datos del perfil de un cliente 
        if path.startswith('/getPerfil'):
            # Paso 1: leer parámetro opcional idCliente desde la query string
            print("[DEBUG] Entrando a /getPerfil")
            query = parse_qs(urlparse(self.path).query)
            raw_id = query.get('idCliente', [None])[0]
            if raw_id:
                # Si viene idCliente válido en la URL, convertirlo a entero
                try:
                    id_int = int(raw_id)
                except ValueError:
                    # Si la conversión falla, ignorar y usar la sesión
                    id_int = None
            else:
                # Si no viene idCliente, obtenerlo directamente de la sesión autenticada
                cliente = self.get_cliente()
                if not cliente: return
                id_int = cliente['id']

            # Paso 2: recuperar datos desde la base de datos
            perfil = obtener_perfil(id_int)
            print(f"[DEBUG] Resultado de obtener_perfil({id_int}): {perfil}")
            if not perfil:
                # Paso 3: si no existe perfil, devolver error 404 
                print("[DEBUG] No se encontró el perfil en la base de datos")
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Cliente no encontrado'}).encode('utf-8'))
                return

            # Paso 4: convertir campos Decimal a tipo float
            if isinstance(perfil.get('saldo'), decimal.Decimal):
                perfil['saldo'] = float(perfil['saldo'])

            # Paso 5: devolver el objeto perfil serializado 
            print(f"[DEBUG] Perfil final a devolver: {perfil}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(perfil).encode('utf-8'))
            return
        
        ########################
        ### GESTIONAR PERFIL ###
        ########################
        # Nuevo endpoint: Obtener historial de descargas del cliente
        if path == '/getHistorial':
            cliente = self.get_cliente()
            if not cliente: return
            historial = obtener_historial(cliente['id'])
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(historial).encode('utf-8'))
            return
        # Nuevo endpoint: Obtener notas del cliente desde BD
        if path == '/getNotas':
            cliente = self.get_cliente()
            if not cliente: return
            notas = obtener_notas(cliente['id'])
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(notas).encode('utf-8'))
            return

        ############################
        ### GESTIONAR CATEGORIAS ###
        ############################

        if path == '/AdminGestorCategorias':
            self.serve_page('AdminGestorCategorias.html')
            return
        
        # --- ENDPOINT: Verificar existencia de categoría ---
        if self.path.startswith('/verificarCategoria'):
            query = parse_qs(urlparse(self.path).query)
            nombre = query.get('nombre', [None])[0]
            padre = query.get('padre', [None])[0]
            resultado = GestorCategorias.verificar_categoria_externa(nombre, padre)
            self.send_response(resultado['status'])
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resultado['data']).encode('utf-8'))
            return
        
        # --- ENDPOINT: Obtener categorías hijas segun un padre ---
        if self.path.startswith('/getCategoriasHijas'):
            query = parse_qs(urlparse(self.path).query)
            padre = query.get('padre', [''])[0]
            categorias = GestorCategorias.obtener_categorias_hijas(padre)
            if categorias is not None:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(categorias).encode('utf-8'))
            else:
                self.send_response(500)
                self.end_headers()
            return
        
        # --- ENDPOINT: Obtener conjunto de categorías ---
        if self.path.startswith('/getCategorias'):
            query = parse_qs(urlparse(self.path).query)
            filter_parent = query.get('filter', [''])[0]
            sort = query.get('sort', ['false'])[0] == 'true'
            categorias = GestorCategorias.obtener_categorias(filter_parent, sort)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(categorias).encode('utf-8'))
            return
        
        ############################
        ### GESTIONAR CONTENIDOS ###
        ############################

        if path == '/AdminGestorContenido':
            self.serve_page('AdminGestorContenido.html')
            return
        
        # --- ENDPOINT: Verificar existencia de contenido ---
        if self.path.startswith('/existeContenido'):
            query = parse_qs(urlparse(self.path).query)
            nombre = query.get('nombre', [''])[0]
            existe = GestorContenido.existe_contenido(nombre)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'existe': existe}).encode('utf-8'))
            return

        # --- ENDPOINT: Obtener contenido por ID ---
        if self.path.startswith('/getContenidoUnique'):
            query = parse_qs(urlparse(self.path).query)
            busqueda = query.get('busqueda', [''])[0]
            contenido = GestorContenido.obtener_contenido_unique(busqueda)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(contenido if contenido else {}).encode('utf-8'))
            return
        
        # --- ENDPOINT: Obtener conjunto de contenidos ---
        if self.path.startswith('/getContenidos'):
            contenidos = GestorContenido.obtener_contenidos()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(contenidos).encode('utf-8'))
            return
        
        #############################
        ### GESTIONAR PROMOCIONES ###
        #############################

        if path == '/AdminGestorPromociones':
            self.serve_page('AdminGestorPromociones.html')
            return
        
        # --- ENDPOINT: Conseguir una promoción por ID ---
        if self.path.startswith('/proGetPromocionById'):
            query = parse_qs(urlparse(self.path).query)
            promo_id = query.get('id', [''])[0]
            try:
                promo_id = int(promo_id)
            except (ValueError, TypeError):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'ID inválido.'}).encode('utf-8'))
                return

            promo = GestorPromociones.obtener_promocion_por_id(promo_id)
            if promo:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(promo).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Promoción no encontrada.'}).encode('utf-8'))
            return
        
        # --- ENDPOINT: Conseguir una promoción por nombre ---
        if self.path.startswith('/proGetPromocionByNombre'):
            query = parse_qs(urlparse(self.path).query)
            nombre = query.get('nombre', [''])[0]
            promo = GestorPromociones.obtener_promocion_por_nombre(nombre)
            if promo:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(promo).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Promoción no encontrada.'}).encode('utf-8'))
            return
        
        # --- ENDPOINT: Obtener todas las promociones ---
        if self.path.startswith('/getPromociones'):
            promociones = GestorPromociones.obtener_promociones()
            if promociones is not None:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(promociones).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Error al obtener promociones.'}).encode('utf-8'))
            return

        # --- ENDPOINT: Obtener promociones activas por autor ---
        if self.path.startswith('/promoGetAutores'):
            autores = GestorPromociones.obtener_autores()
            if autores is not None:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(autores).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Error al obtener autores.'}).encode('utf-8'))
            return
        
        # --- ENDPOINT: Obtener categorías para promociones ---
        if self.path.startswith('/promoGetCategorias'):
            categorias = GestorPromociones.obtener_categorias()
            if categorias is not None:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(categorias).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Error al obtener categorías.'}).encode('utf-8'))
            return

        # --- ENDPOINT: Obtener contenidos por autor y promociones---
        if self.path.startswith('/promoGetContenidosPorAutor'):
            query = parse_qs(urlparse(self.path).query)
            autor = query.get('autor', [''])[0]
            contenidos = GestorPromociones.obtener_contenidos_por_autor(autor)
            if contenidos is not None:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(contenidos).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Error al obtener contenidos.'}).encode('utf-8'))
            return
        
        # --- ENDPOINT: Obtener contenidos por categoría y subcategorías ---
        if self.path.startswith('/promoGetContenidosPorCategoria'):
            query = parse_qs(urlparse(self.path).query)
            categoria = query.get('categoria', [''])[0]
            contenidos = GestorPromociones.obtener_contenidos_por_categoria_y_subcategorias(categoria)
            if contenidos is not None:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(contenidos).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Error al obtener contenidos.'}).encode('utf-8'))
            return
        
        # --- ENDPOINT: Obtener contenidos por promoción ---
        if self.path.startswith('/promGetContenidosPorPromocion'):
            query = parse_qs(urlparse(self.path).query)
            promo_id = query.get('id', [''])[0]
            contenidos = GestorPromociones.obtener_contenidos_por_promocion(promo_id)
            if contenidos is not None:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(contenidos).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Error al obtener contenidos.'}).encode('utf-8'))
            return
        
        ####################
        ### CARGAR SALDO ###
        ####################
        if path == '/CargarSaldo':
            self.serve_page('CargarSaldo.html')
            return

        # Manejar la ruta de logout
        if path == '/logout':
            self.redirect('/')
            return

        if self.path.startswith('/.well-known/'):
            self.send_response(204)  # No Content
            self.end_headers()
            return
        
        # Si la ruta no coincide con ninguna, devolver un error 404
        self.send_error(404, "Página no encontrada")

    def serve_page(self, template_name, cliente=None):
        """Sirve una página HTML desde la carpeta de plantillas."""
        try:
            # Cargar la plantilla HTML
            with open(os.path.join('templates', template_name), 'r', encoding='utf-8') as f:
                html = f.read()

            # Inyectar id_cliente en plantilla si está disponible
            if cliente is not None:
                # Inyectar ID y username en la plantilla
                html = html.replace('{{ID_CLIENTE}}', str(cliente['id']))
                html = html.replace('{{USERNAME}}', cliente['username'])
                # Inyectar nombre completo del cliente
                html = html.replace('{{NOMBRE}}', cliente.get('nombre', cliente['username']))

            # Enviar la respuesta al cliente
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "Archivo no encontrado")

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
    
    

    def redirect(self, location):
        self.send_response(302)
        self.send_header('Location', location)
        self.end_headers()

    def do_POST(self):
        if self.path == '/login':
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = dict(x.split('=') for x in post_data.split('&'))
            username = params.get('username')
            password = params.get('password')

            try:
                conexion = mysql.connector.connect(**DB_CONFIG)
                cursor = conexion.cursor(dictionary=True)

                # Intentar iniciar sesión como administrador
                cursor.execute(
                    "SELECT * FROM TablaUsuarios WHERE username_ = %s AND password_ = %s",
                    (username, password)
                )
                usuario_admin = cursor.fetchone()
                if usuario_admin:
                    self.redirect('/AdminPaginaPrincipal')
                    return

                # Intentar iniciar sesión como cliente
                cursor.execute(
                    "SELECT * FROM TablaCliente WHERE username = %s AND password = %s AND estado = 'cliente'",
                    (username, password)
                )
                cliente = cursor.fetchone()
                if cliente:
                    # Crear sesión cliente y setear cookie
                    sid = crear_sesion(cliente)
                    self.send_response(302)
                    self.send_header('Set-Cookie', f'session_id={sid}; HttpOnly; Path=/')
                    self.send_header('Location', '/ClientePaginaPrincipal')
                    self.end_headers()
                    return
                else:
                    # Credenciales incorrectas
                    self.send_response(401)
                    self.send_header('Content-Type', 'text/plain; charset=utf-8')
                    self.end_headers()
                    self.wfile.write(b"Credenciales incorrectas")
            except mysql.connector.Error as err:
                self.send_error(500, f"Error de MySQL: {err}")
            finally:
                if 'cursor' in locals():
                    cursor.close()
                if 'conexion' in locals():
                    conexion.close()
            return
        
        ############################
        ### GESTIONAR CATEGORIAS ###
        ############################
        
        # --- ENDPOINT: Agregar Categoría ---
        elif self.path == '/agregarCategoria':
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

            resultado = GestorCategorias.agregar_categoria({'nombre': nombre, 'categoria_padre': categoria_padre})
            if resultado['ok']:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'mensaje': resultado['mensaje']}).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': resultado['error']}).encode('utf-8'))
            return

        # --- ENDPOINT: Eliminar Categoría ---
        elif self.path == '/eliminarCategoria':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)

            nombre = data.get('nombre')
            categoria_padre = data.get('categoria_padre')

            resultado = GestorCategorias.eliminar_categoria({'nombre': nombre, 'categoria_padre': categoria_padre})
            if resultado['ok']:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'mensaje': resultado['mensaje']}).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': resultado['error']}).encode('utf-8'))
            return
        
        # --- ENDPOINT: Editar Categoría ---
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

            resultado = GestorCategorias.editar_categoria({'nombre_actual': nombre_actual, 'nuevo_nombre': nuevo_nombre})
            if resultado['ok']:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'mensaje': resultado['mensaje']}).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': resultado['error']}).encode('utf-8'))
            return
        
        ############################
        ### GESTIONAR CONTENIDOS ###
        ############################

        # --- ENDPOINT: Agregar Contenido ---
        elif self.path == '/agregarContenido':
            content_length = int(self.headers['Content-Length'])
            content_type = self.headers.get('Content-Type', '')

            if 'multipart/form-data' in content_type:
                import cgi
                env = {'REQUEST_METHOD': 'POST'}
                fs = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ=env,
                    keep_blank_values=True
                )
                data = {
                    'nombre': fs.getvalue('nombre'),
                    'autor': fs.getvalue('autor'),
                    'descripcion': fs.getvalue('descripcion'),
                    'tipo': fs.getvalue('tipo'),
                    'precio': fs.getvalue('precio'),
                    'extension': fs.getvalue('extension'),
                    'mime': fs.getvalue('mime'),
                    'calificacion': 0
                }
                archivo_field = fs['archivo'] if 'archivo' in fs else None
                archivo_binario = archivo_field.file.read() if archivo_field is not None else None

                if not all([data['nombre'], data['autor'], data['descripcion'], data['tipo'], data['precio'], archivo_binario]):
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Faltan campos obligatorios'}).encode('utf-8'))
                    return
                # Testear subiendo todos los tipos de archivos
                extensiones_permitidas = ['jpg', 'jpeg', 'png', 'mp3', 'flac', 'wav', 'mp4']
                mimes_permitidos = [
                    'image/jpeg', 'image/png',
                    'audio/mpeg', 'audio/flac', 'audio/wav',
                    'video/mp4'
                ]
                if data['extension'] not in extensiones_permitidas or data['mime'] not in mimes_permitidos:
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Formato de archivo no permitido.'}).encode('utf-8'))
                    return
                resultado = GestorContenido.agregar_contenido(data, archivo_binario)
                if resultado:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'mensaje': 'Contenido agregado correctamente.'}).encode('utf-8'))
                else:
                    self.send_response(500)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'error': 'Error al agregar el contenido.'}).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Tipo de contenido no soportado.'}).encode('utf-8'))

        # --- ENDPOINT: Obtener contenido por ID o nombre ---
        elif self.path.startswith('/getContenido'):
            query = parse_qs(urlparse(self.path).query)
            busqueda = query.get('busqueda', [''])[0]
            contenido = GestorContenido.obtener_contenido(busqueda)
            if contenido:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(contenido).encode('utf-8'))
            else:
                self.send_response(404)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'No se encontró el contenido.'}).encode('utf-8'))
            return

        # --- ENDPOINT: Editar Contenido ---
        elif self.path == '/editarContenido':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            contenido_id = data.get('id')
            nuevo_nombre = data.get('nombre')
            descripcion = data.get('descripcion')
            precio = data.get('precio')
            autor = data.get('autor')
            if not contenido_id or not nuevo_nombre or not descripcion or not precio or not autor:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Faltan parámetros'}).encode('utf-8'))
                return

            resultado = GestorContenido.editar_contenido(contenido_id, nuevo_nombre, descripcion, precio, autor)
            if resultado['ok']:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'mensaje': resultado['mensaje']}).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': resultado['error']}).encode('utf-8'))
            return
        
        # --- ENDPOINT: Eliminar Contenido ---
        elif self.path == '/eliminarContenido':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            contenido_id = data.get('id')
            resultado = GestorContenido.eliminar_contenido(contenido_id)
            if resultado['ok']:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'mensaje': resultado['mensaje']}).encode('utf-8'))
            else:
                self.send_response(404 if resultado['error'] == 'Contenido no encontrado.' else 500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': resultado['error']}).encode('utf-8'))
            return

        #############################
        ### GESTIONAR PROMOCIONES ###
        #############################

        # --- ENDPOINT: Agregar Promoción ---
        elif self.path == '/agregarPromocion':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            nombre = data.get('nombre')
            descripcion = data.get('descripcion')
            fecha_inicio = data.get('fecha_inicio')
            fecha_fin = data.get('fecha_fin')
            porcentaje = data.get('porcentaje')
            modo = data.get('modo')
            valor = data.get('valor')

            if not (nombre and descripcion and fecha_inicio and fecha_fin and porcentaje and modo and valor):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Faltan parámetros'}).encode('utf-8'))
                return

            resultado = GestorPromociones.agregar_promocion(nombre, descripcion, fecha_inicio, fecha_fin, porcentaje, modo, valor)
            if resultado['ok']:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'mensaje': resultado['mensaje']}).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': resultado['error']}).encode('utf-8'))
            return
        
        # --- ENDPOINT: Editar Promoción ---
        elif self.path == '/editarPromocion':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            promo_id = data.get('id')
            nombre = data.get('nombre')
            descripcion = data.get('descripcion')
            fecha_inicio = data.get('fecha_inicio')
            fecha_fin = data.get('fecha_fin')
            porcentaje = data.get('porcentaje')
            if not (promo_id and nombre and descripcion and fecha_inicio and fecha_fin and porcentaje):
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Todos los campos son obligatorios.'}).encode('utf-8'))
                return

            resultado = GestorPromociones.editar_promocion(promo_id, nombre, descripcion, fecha_inicio, fecha_fin, porcentaje)
            if resultado['ok']:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'mensaje': resultado['mensaje']}).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': resultado['error']}).encode('utf-8'))
            return

        # --- ENDPOINT: Eliminar Promoción ---
        elif self.path == '/eliminarPromocion':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            promo_id = data.get('id')
            if not promo_id:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'ID de promoción requerido.'}).encode('utf-8'))
                return

            resultado = GestorPromociones.eliminar_promocion(promo_id)
            if resultado['ok']:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'mensaje': resultado['mensaje']}).encode('utf-8'))
            else:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': resultado['error']}).encode('utf-8'))
            return
        
        ############################
        ### GESTIONAR PERFIL ###
        ############################
        if self.path == '/actualizarPerfil':
            print("[DEBUG] Entrando a /actualizarPerfil")
            # 1) Verificar que venga como application/x-www-form-urlencoded
            content_type = self.headers.get('Content-Type', '')
            print(f"[DEBUG] Content-Type recibido: {content_type}")
            if not content_type.startswith('application/x-www-form-urlencoded'):
                print("[DEBUG] Content-Type incorrecto")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'Content-Type incorrecto. Debe ser application/x-www-form-urlencoded.'
                }).encode('utf-8'))
                return

            # 2) Leer todo el cuerpo y decodificar a string
            longitud = int(self.headers.get('Content-Length', 0))
            cuerpo_bytes = self.rfile.read(longitud)
            cuerpo_str = cuerpo_bytes.decode('utf-8')
            print(f"[DEBUG] Cuerpo recibido: {cuerpo_str}")

            # 3) Parsear los campos
            datos = parse_qs(cuerpo_str, keep_blank_values=True)
            print(f"[DEBUG] Datos parseados: {datos}")
            id_cliente = datos.get('idCliente', [None])[0]
            nuevo_nombre = datos.get('nombre', [None])[0]
            nuevo_correo = datos.get('correo', [None])[0]
            contrasena_anterior = datos.get('contrasena_anterior', [None])[0]
            nueva_contrasena = datos.get('nueva_contrasena', [None])[0]

            # 4) Verificar que no falten los obligatorios
            if not id_cliente or not nuevo_nombre or not nuevo_correo or not contrasena_anterior:
                print("[DEBUG] Faltan campos obligatorios")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'Faltan campos obligatorios en perfil.'
                }).encode('utf-8'))
                return

            # 5) Convertir idCliente a entero
            try:
                id_int = int(id_cliente)
                print(f"[DEBUG] id_cliente convertido a int: {id_int}")
            except ValueError:
                print("[DEBUG] idCliente no es un entero")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': 'idCliente debe ser un número entero.'
                }).encode('utf-8'))
                return

            # 6) Si nueva_contrasena viene como cadena vacía, tratarla como None
            if nueva_contrasena == '':
                nueva_contrasena = None

            print(f"[DEBUG] Llamando a editar_perfil con: id_cliente={id_int}, nuevo_nombre={nuevo_nombre}, nuevo_correo={nuevo_correo}, contrasena_anterior={contrasena_anterior}, nueva_contrasena={nueva_contrasena}")

            # 7) Llamar a editar_perfil() sin foto
            exito, mensaje = editar_perfil(
                id_cliente=id_int,
                nuevo_nombre=nuevo_nombre,
                nuevo_correo=nuevo_correo,
                contrasena_anterior=contrasena_anterior,
                nueva_contrasena=nueva_contrasena
            )

            print(f"[DEBUG] Resultado editar_perfil: exito={exito}, mensaje={mensaje}")

            if exito:
                print("[DEBUG] Perfil actualizado correctamente, enviando JSON de éxito")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'success': True, 'mensaje': mensaje}).encode('utf-8'))
            else:
                print("[DEBUG] Error al actualizar perfil")
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'error': mensaje
                }).encode('utf-8'))
            return

def ejecutar_servidor(puerto=8000):
    servidor = HTTPServer(('', puerto), Manejador)
    print(f'Servidor en http://localhost:{puerto}')
    servidor.serve_forever()

if __name__ == '__main__':
    ejecutar_servidor()