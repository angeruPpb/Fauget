import mysql.connector
import decimal
from gestorConfig import DB_CONFIG
import datetime

class GestorContenido:
    @staticmethod
    def agregar_contenido(data, archivo_binario=None):
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            # 1. Insertar el contenido SIN promocion_id
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

            # 2. Buscar promociones activas por autor o categoría
            cursor2 = conexion.cursor(dictionary=True)
            hoy = datetime.date.today().isoformat()
            # Buscar promociones por autor
            cursor2.execute("""
                SELECT id, porcentaje FROM TablaPromocion
                WHERE fecha_inicio <= %s AND fecha_fin >= %s AND id IN (
                    SELECT promocion_id FROM TablaContenido WHERE autor = %s
                )
            """, (hoy, hoy, data.get('autor')))
            promos_autor = cursor2.fetchall()

            # Buscar promociones por categoría y subcategorías
            def obtener_categorias_hijas(cat):
                cursor2.execute("SELECT nombre FROM TablaCategorias WHERE categoria_padre = %s", (cat,))
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
                WHERE fecha_inicio <= %s AND fecha_fin >= %s AND id IN (
                    SELECT promocion_id FROM TablaContenido WHERE categoria IN ({formato})
                )
            """, tuple([hoy, hoy] + categorias))
            promos_categoria = cursor2.fetchall()

            # 3. Elegir la promoción de mayor porcentaje
            todas = promos_autor + promos_categoria
            if todas:
                mejor = max(todas, key=lambda p: p['porcentaje'])
                cursor.execute("UPDATE TablaContenido SET promocion_id = %s WHERE id = %s", (mejor['id'], contenido_id))
            conexion.commit()
            return True
        except Exception as err:
            print(f"Error al agregar contenido: {err}")
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'cursor2' in locals(): cursor2.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def editar_contenido(nombre_actual, nuevo_nombre, autor, descripcion, precio):
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            sql = """
                UPDATE TablaContenido
                SET nombre = %s, autor = %s, descripcion = %s, precio = %s
                WHERE nombre = %s
            """
            valores = (nuevo_nombre, autor, descripcion, precio, nombre_actual)
            cursor.execute(sql, valores)
            conexion.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al editar contenido: {err}")
            return False
        finally:
            if 'cursor' in locals: cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def eliminar_contenido(nombre):
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            sql = "DELETE FROM TablaContenido WHERE nombre = %s"
            cursor.execute(sql, (nombre,))
            conexion.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as err:
            print(f"Error al eliminar contenido: {err}")
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()


def obtener_contenidos():
    """Devuelve una lista de contenidos con id, nombre, autor, descripcion y precio (precio como float)."""
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, autor, descripcion, precio FROM TablaContenido")
        contenidos = cursor.fetchall()
        # Convertir Decimal a float para el campo precio
        for c in contenidos:
            if isinstance(c['precio'], decimal.Decimal):
                c['precio'] = float(c['precio'])
        return contenidos
    except mysql.connector.Error as err:
        print(f"Error al obtener contenidos: {err}")
        return []
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()

def obtener_contenido_unique(busqueda):
    """Devuelve la información de un contenido por ID o nombre (case sensitive)."""
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor(dictionary=True)
        if str(busqueda).isdigit():
            cursor.execute("SELECT id, nombre, autor, descripcion, precio FROM TablaContenido WHERE id = %s", (busqueda,))
        else:
            cursor.execute("SELECT id, nombre, autor, descripcion, precio FROM TablaContenido WHERE nombre = %s", (busqueda,))
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


def existe_contenido(nombre):
    try:
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor()
        cursor.execute("SELECT COUNT(*) FROM TablaContenido WHERE nombre = %s", (nombre,))
        existe = cursor.fetchone()[0] > 0
        return existe
    except Exception as e:
        print(f"Error al verificar contenido: {e}")
        return False
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conexion' in locals(): conexion.close()