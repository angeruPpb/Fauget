import mysql.connector
import decimal
from gestorConfig import DB_CONFIG
import datetime

'''
Gestor Proociones (OG11)
Modifica las tablas TablaPromocion (OE08) y TablaContenido (OE07) 
Funciones:
- agregar_promocion: Agrega una nueva promoción y la aplica a los contenidos afectados.
- editar_promocion: Edita una promoción existente.
- eliminar_promocion: Elimina una promoción y quita su asociación de los contenidos.
- obtener_promocion_por_id: Obtiene una promoción por su ID.
- obtener_promocion_por_nombre: Obtiene una promoción por su nombre.
- obtener_promociones: Obtiene todas las promociones.
- obtener_autores: Obtiene una lista de autores únicos de la tabla de contenidos.
- obtener_categorias: Obtiene una lista de nombres de categorías.
- obtener_contenidos_por_autor: Obtiene contenidos filtrados por autor.
- obtener_contenidos_por_categoria_y_subcategorias: Obtiene contenidos de una categoría y todas sus subcategorías.
- obtener_contenidos_por_promocion: Obtiene contenidos asociados a una promoción.
'''
class GestorPromociones:
    @staticmethod
    def agregar_promocion(nombre, descripcion, fecha_inicio, fecha_fin, porcentaje, modo, valor):
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)

            # Crear la promoción
            cursor.execute(
                "INSERT INTO TablaPromocion (nombre, porcentaje, descripcion, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s, %s)",
                (nombre, porcentaje, descripcion, fecha_inicio, fecha_fin)
            )
            conexion.commit()
            promo_id = cursor.lastrowid

            # Buscar los contenidos afectados
            if modo == 'autor':
                cursor.execute("SELECT id, promocion_id FROM TablaContenido WHERE autor = %s", (valor,))
                contenidos = cursor.fetchall()
            elif modo == 'categoria':
                # Obtener todas las categorías hijas recursivamente
                def obtener_categorias_hijas(nombre_categoria):
                    cursor.execute("SELECT nombre FROM TablaCategorias WHERE categoria_padre = %s", (nombre_categoria,))
                    hijas = [row['nombre'] for row in cursor.fetchall()]
                    todas = []
                    for hija in hijas:
                        todas.append(hija)
                        todas += obtener_categorias_hijas(hija)
                    return todas

                categorias = [valor] + obtener_categorias_hijas(valor)
                formato = ','.join(['%s'] * len(categorias))
                cursor.execute(f"SELECT id, promocion_id FROM TablaContenido WHERE categoria IN ({formato})", tuple(categorias))
                contenidos = cursor.fetchall()
            else:
                contenidos = []

            # Para cada contenido, asignar la promoción si corresponde
            for contenido in contenidos:
                contenido_id = contenido['id']
                promocion_actual_id = contenido['promocion_id']

                aplicar_nueva = True
                if promocion_actual_id:
                    cursor.execute("SELECT porcentaje FROM TablaPromocion WHERE id = %s", (promocion_actual_id,))
                    promo_actual = cursor.fetchone()
                    if promo_actual and promo_actual['porcentaje'] >= porcentaje:
                        aplicar_nueva = False  # No reemplazar si la actual es mayor o igual

                if aplicar_nueva:
                    cursor.execute("UPDATE TablaContenido SET promocion_id = %s WHERE id = %s", (promo_id, contenido_id))

            conexion.commit()
            return {'ok': True, 'mensaje': 'Promoción agregada y aplicada correctamente.'}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def editar_promocion(promo_id, nombre, descripcion, fecha_inicio, fecha_fin, porcentaje):
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            cursor.execute(
                "UPDATE TablaPromocion SET nombre=%s, descripcion=%s, fecha_inicio=%s, fecha_fin=%s, porcentaje=%s WHERE id=%s",
                (nombre, descripcion, fecha_inicio, fecha_fin, porcentaje, promo_id)
            )
            conexion.commit()
            return {'ok': True, 'mensaje': 'Promoción editada correctamente.'}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def eliminar_promocion(promo_id):
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            # Eliminar la promoción de los contenidos
            cursor.execute("UPDATE TablaContenido SET promocion_id = NULL WHERE promocion_id = %s", (promo_id,))
            # En lugar de eliminar la promoción de la tabla de promociones
            cursor.execute("UPDATE TablaPromocion SET estado = 0 WHERE id = %s", (promo_id,))
            conexion.commit()
            return {'ok': True, 'mensaje': 'Promoción eliminada correctamente.'}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def obtener_promocion_por_id(promo_id):
        """Devuelve la promoción por id o None si no existe."""
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, nombre, descripcion, fecha_inicio, fecha_fin, porcentaje FROM TablaPromocion WHERE id = %s",
                (promo_id,)
            )
            promo = cursor.fetchone()
            if promo:
                # Formatear fechas y porcentaje si es necesario
                if isinstance(promo['fecha_inicio'], (datetime.date, datetime.datetime)):
                    promo['fecha_inicio'] = promo['fecha_inicio'].isoformat()
                if isinstance(promo['fecha_fin'], (datetime.date, datetime.datetime)):
                    promo['fecha_fin'] = promo['fecha_fin'].isoformat()
                if isinstance(promo['porcentaje'], decimal.Decimal):
                    promo['porcentaje'] = float(promo['porcentaje'])
            return promo
        except Exception as e:
            print(f"[DEBUG] Excepción en obtener_promocion_por_id: {e}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def obtener_promocion_por_nombre(nombre):
        """Devuelve la promoción por nombre o None si no existe."""
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, nombre, descripcion, fecha_inicio, fecha_fin, porcentaje FROM TablaPromocion WHERE nombre = %s",
                (nombre,)
            )
            promo = cursor.fetchone()
            if promo:
                # Formatear fechas y porcentaje si es necesario
                if isinstance(promo['fecha_inicio'], (datetime.date, datetime.datetime)):
                    promo['fecha_inicio'] = promo['fecha_inicio'].isoformat()
                if isinstance(promo['fecha_fin'], (datetime.date, datetime.datetime)):
                    promo['fecha_fin'] = promo['fecha_fin'].isoformat()
                if isinstance(promo['porcentaje'], decimal.Decimal):
                    promo['porcentaje'] = float(promo['porcentaje'])
            return promo
        except Exception as e:
            print(f"[DEBUG] Excepción en obtener_promocion_por_nombre: {e}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def obtener_promociones():
        """Devuelve una lista de todas las promociones."""
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT id, nombre, descripcion, porcentaje, fecha_inicio, fecha_fin
                FROM TablaPromocion
            """)
            promociones = cursor.fetchall()
            # Formatear fechas y porcentaje si es necesario
            for promo in promociones:
                if isinstance(promo['fecha_inicio'], (datetime.date, datetime.datetime)):
                    promo['fecha_inicio'] = promo['fecha_inicio'].isoformat()
                if isinstance(promo['fecha_fin'], (datetime.date, datetime.datetime)):
                    promo['fecha_fin'] = promo['fecha_fin'].isoformat()
                if isinstance(promo['porcentaje'], decimal.Decimal):
                    promo['porcentaje'] = float(promo['porcentaje'])
            return promociones
        except Exception as e:
            print(f"[DEBUG] Excepción en obtener_promociones: {e}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def obtener_autores():
        """Devuelve una lista de autores únicos de la tabla de contenidos."""
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            cursor.execute("SELECT DISTINCT autor FROM TablaContenido")
            autores = [{'autor': row[0]} for row in cursor.fetchall()]
            return autores
        except Exception as e:
            print(f"[DEBUG] Excepción en obtener_autores: {e}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def obtener_categorias():
        """Devuelve una lista de nombres de categorías."""
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            cursor.execute("SELECT nombre FROM TablaCategorias")
            categorias = [{'nombre': row[0]} for row in cursor.fetchall()]
            return categorias
        except Exception as e:
            print(f"[DEBUG] Excepción en obtener_categorias: {e}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def obtener_contenidos_por_autor(autor):
        """Devuelve una lista de contenidos filtrados por autor."""
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, autor FROM TablaContenido WHERE autor = %s", (autor,))
            contenidos = cursor.fetchall()
            return contenidos
        except Exception as e:
            print(f"[DEBUG] Excepción en obtener_contenidos_por_autor: {e}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def obtener_contenidos_por_categoria_y_subcategorias(categoria):
        """Devuelve contenidos de una categoría y todas sus subcategorías."""
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)

            # Función recursiva para obtener todas las subcategorías
            def obtener_subcategorias(cat):
                cursor.execute("SELECT nombre FROM TablaCategorias WHERE categoria_padre = %s", (cat,))
                hijas = [row['nombre'] for row in cursor.fetchall()]
                todas = []
                for hija in hijas:
                    todas.append(hija)
                    todas += obtener_subcategorias(hija)
                return todas

            categorias = [categoria] + obtener_subcategorias(categoria)
            formato = ','.join(['%s'] * len(categorias))
            cursor.execute(f"SELECT id, nombre, autor FROM TablaContenido WHERE categoria IN ({formato})", tuple(categorias))
            contenidos = cursor.fetchall()
            return contenidos
        except Exception as e:
            print(f"[DEBUG] Excepción en obtener_contenidos_por_categoria_y_subcategorias: {e}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def obtener_contenidos_por_promocion(promo_id):
        """Devuelve una lista de contenidos asociados a una promoción."""
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT nombre, autor FROM TablaContenido WHERE promocion_id = %s", (promo_id,))
            contenidos = cursor.fetchall()
            return contenidos
        except Exception as e:
            print(f"[DEBUG] Excepción en obtener_contenidos_por_promocion: {e}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()