import mysql.connector
import decimal
from gestorConfig import DB_CONFIG
import datetime

class GestorPromociones:
    @staticmethod
    def agregar_promocion(nombre, descripcion, fecha_inicio, fecha_fin, porcentaje, modo, valor):
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)

            # 1. Crear la promoción
            cursor.execute(
                "INSERT INTO TablaPromocion (nombre, porcentaje, descripcion, fecha_inicio, fecha_fin) VALUES (%s, %s, %s, %s, %s)",
                (nombre, porcentaje, descripcion, fecha_inicio, fecha_fin)
            )
            conexion.commit()
            promo_id = cursor.lastrowid

            # 2. Buscar los contenidos afectados
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

            # 3. Para cada contenido, asignar la promoción si corresponde
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
            # Eliminar la promoción de la tabla de promociones
            cursor.execute("DELETE FROM TablaPromocion WHERE id = %s", (promo_id,))
            conexion.commit()
            return {'ok': True, 'mensaje': 'Promoción eliminada correctamente.'}
        except Exception as e:
            return {'ok': False, 'error': str(e)}
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()