import mysql.connector
import decimal
from gestorConfig import DB_CONFIG
import datetime

'''
Gestor de Contenido (OG09)
Modifica las tablas TablaContenido (OE07), TablaPromocion (OE08) y ContenidoCliente (OE10).
Funciones:
- (FA001) agregar_contenido: Inserta un nuevo contenido y asigna la mejor promoción.  
- (FA002) editar_contenido: Actualiza un contenido existente.                       
- (FA003) eliminar_contenido: Elimina un contenido y notifica a los usuarios afectados.
- (FA004) obtener_contenidos: Devuelve una lista de todos los contenidos.               
- (FA005) obtener_contenido_unique: Devuelve un contenido por ID o nombre (case sensitive).
- (FA006) existe_contenido: Verifica si un contenido con un nombre específico ya existe.
- (FA007) obtener_contenido: Devuelve un contenido por ID o nombre.
'''

class GestorContenido:
    @staticmethod #FA001
    def agregar_contenido(data, archivo_binario=None): 
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            sql = """
                INSERT INTO TablaContenido
                (nombre, autor, descripcion, tipo, categoria, extension, mime, precio, calificacion, archivo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            valores = (
                data.get('nombre'),
                data.get('autor'),
                data.get('descripcion'),
                data.get('tipo'),
                data.get('categoria'),
                data.get('extension'),
                data.get('mime'),
                data.get('precio'),
                data.get('calificacion', 0),
                archivo_binario
            )
            cursor.execute(sql, valores)
            contenido_id = cursor.lastrowid

            cursor2 = conexion.cursor(dictionary=True)
            hoy = datetime.date.today().isoformat()
            # Buscar promociones por autor
            cursor2.execute("""
                SELECT id, porcentaje FROM TablaPromocion
                WHERE fecha_inicio <= %s AND fecha_fin >= %s AND id IN (
                    SELECT promocion_id FROM TablaContenido WHERE autor = %s AND estado = 1
                )
            """, (hoy, hoy, data.get('autor')))
            promos_autor = cursor2.fetchall()

            # Buscar promociones por categoría y subcategorías
            def obtener_categorias_hijas(cat):
                cursor2.execute("SELECT nombre FROM TablaCategorias WHERE categoria_padre = %s AND estado = 1", (cat,))
                hijas = [row['nombre'] for row in cursor2.fetchall()]
                todas = []
                for hija in hijas:
                    todas.append(hija)
                    todas += obtener_categorias_hijas(hija)
                return todas

            categorias = [data.get('categoria')] + obtener_categorias_hijas(data.get('categoria'))
            formato = ','.join(['%s'] * len(categorias))
            cursor2.execute(f"""
                SELECT id, porcentaje FROM TablaPromocion
                WHERE fecha_inicio <= %s AND fecha_fin >= %s AND estado = 1 AND id IN (
                    SELECT promocion_id FROM TablaContenido WHERE categoria IN ({formato})
                )
            """, tuple([hoy, hoy] + categorias))
            promos_categoria = cursor2.fetchall()

            # Elegir la promoción de mayor porcentaje
            todas = promos_autor + promos_categoria
            if todas:
                mejor = max(todas, key=lambda p: p['porcentaje'])
                cursor.execute("UPDATE TablaContenido SET promocion_id = %s WHERE id = %s AND estado = 1", (mejor['id'], contenido_id))
            conexion.commit()
            return True
        except Exception as err:
            print(f"Error al agregar contenido: {err}")
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'cursor2' in locals(): cursor2.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod #FA002
    def editar_contenido(contenido_id, nuevo_nombre, descripcion, precio, autor):
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)
            # Verificar duplicado
            cursor.execute("SELECT id FROM TablaContenido WHERE nombre = %s AND id != %s AND estado = 1", (nuevo_nombre, contenido_id))
            duplicado = cursor.fetchone()
            if duplicado:
                return {'ok': False, 'error': 'Ya existe otro contenido con ese nombre.'}
            # Actualizar contenido
            cursor.execute(
                "UPDATE TablaContenido SET nombre = %s, descripcion = %s, precio = %s, autor = %s WHERE id = %s AND estado = 1",
                (nuevo_nombre, descripcion, precio, autor, contenido_id)
            )
            conexion.commit()
            return {'ok': True, 'mensaje': 'Contenido editado correctamente.'}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod #FA003
    def eliminar_contenido(contenido_id):
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)
            # Obtener nombre del contenido
            cursor.execute("SELECT nombre FROM TablaContenido WHERE id = %s AND estado = 1", (contenido_id,))
            row = cursor.fetchone()
            print(f"id del contenido a eliminar: {contenido_id}")
            print(f"Contenido a eliminar: {row}")
            if not row:
                return {'ok': False, 'error': 'Contenido no encontrado.'}
            nombre_contenido = row['nombre']

            # Buscar todos los usuarios que tengan el contenido
            cursor.execute("SELECT usuario_id FROM ContenidoCliente WHERE contenido_id = %s", (contenido_id,))
            usuarios = cursor.fetchall()
            for usuario in usuarios:
                mensaje = f"Lamentamos informarle que el contenido '{nombre_contenido}' ha sido retirado de la plataforma. Disculpe las molestias."
                cursor.execute(
                    "INSERT INTO Notificacion (usuario_id, emisor, mensaje) VALUES (%s, %s, %s)",
                    (usuario['usuario_id'], 'Sistema', mensaje)
                )
            # Eliminar el contenido de la tabla de los usuarios
            cursor.execute("DELETE FROM ContenidoCliente WHERE contenido_id = %s", (contenido_id,))
            # Cambiar el estado del contenido a 0 (inactivo) en vez de eliminarlo
            cursor.execute("UPDATE TablaContenido SET estado = 0 WHERE id = %s", (contenido_id,))
            conexion.commit()
            return {'ok': True, 'mensaje': 'Contenido eliminado correctamente.'}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod #FA004
    def obtener_contenidos():
        """Devuelve una lista de contenidos con info básica y porcentaje de promoción activa si la tiene."""
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)
            hoy = datetime.date.today().isoformat()
            cursor.execute("""
            SELECT c.id, c.nombre, c.autor, c.descripcion, c.categoria, c.precio,
                CASE
                    WHEN p.id IS NOT NULL
                         AND %s BETWEEN p.fecha_inicio AND p.fecha_fin
                         AND p.estado = 1
                    THEN p.porcentaje
                    ELSE NULL
                END AS promocion_activa_porcentaje
            FROM TablaContenido c
            LEFT JOIN TablaPromocion p ON c.promocion_id = p.id
            WHERE c.estado = 1
              """, (hoy,))
            contenidos = cursor.fetchall()
            # Convertir Decimal a float para el campo precio y porcentaje
            for c in contenidos:
                if isinstance(c['precio'], decimal.Decimal):
                    c['precio'] = float(c['precio'])
                if c.get('promocion_activa_porcentaje') is not None and isinstance(c['promocion_activa_porcentaje'], decimal.Decimal):
                    c['promocion_activa_porcentaje'] = float(c['promocion_activa_porcentaje'])
            return contenidos
        except mysql.connector.Error as err:
            print(f"Error al obtener contenidos: {err}")
            return []
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()
    
    @staticmethod #FA005
    def obtener_contenido_unique(busqueda):
        """Devuelve la información de un contenido por ID o nombre (case sensitive)."""
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)
            if str(busqueda).isdigit():
                cursor.execute("SELECT id, nombre, autor, descripcion, precio FROM TablaContenido WHERE id = %s AND estado = 1", (busqueda,))
            else:
                cursor.execute("SELECT id, nombre, autor, descripcion, precio FROM TablaContenido WHERE nombre = %s AND estado = 1", (busqueda,))
            contenido = cursor.fetchone()
            if contenido and isinstance(contenido['precio'], decimal.Decimal):
                contenido['precio'] = float(contenido['precio'])
            return contenido
        except mysql.connector.Error as err:
            print(f"Error al obtener contenido: {err}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod #FA006
    def existe_contenido(nombre):
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            cursor.execute("SELECT COUNT(*) FROM TablaContenido WHERE nombre = %s AND estado = 1", (nombre,))
            existe = cursor.fetchone()[0] > 0
            return existe
        except Exception as e:
            print(f"Error al verificar contenido: {e}")
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()
    
    @staticmethod #FA007
    def obtener_contenido(busqueda):
        """Devuelve un contenido por id (si es dígito) o por nombre."""
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)
            if str(busqueda).isdigit():
                cursor.execute("SELECT * FROM TablaContenido WHERE id = %s AND estado = 1", (busqueda,))
            else:
                cursor.execute("SELECT * FROM TablaContenido WHERE nombre = %s AND estado = 1", (busqueda,))
            contenido = cursor.fetchone()
            return contenido
        except Exception as e:
            print(f"Error al obtener contenido: {e}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()