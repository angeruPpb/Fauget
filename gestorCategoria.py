import mysql.connector
from gestorConfig import DB_CONFIG

'''
Gestor de Categorías (OG18)
Modifica las tablas TablaCategorias (OE14) y TablaContenidos (OE07)
Funciones:
- agregar_categoria(data): Agrega una nueva categoría a la base de datos.
- eliminar_categoria(data): Elimina una categoría y reasigna sus contenidos a la categoría padre.
- editar_categoria(data): Edita el nombre de una categoría existente.
- verificar_categoria(nombre, padre): Verifica si una categoría existe dado su nombre y padre.
- verificar_categoria_externa(nombre, padre): Verifica si una categoría existe externamente.
- obtener_categorias(filter_parent='', sort=False): Obtiene una lista de categorías, opcionalmente filtradas por padre y ordenadas por nombre.
- obtener_categorias_hijas(padre): Obtiene las categorías hijas de una categoría dada.
'''

class GestorCategorias: 
    @staticmethod
    def agregar_categoria(data):
        nombre = data['nombre']
        categoria_padre = data['categoria_padre']
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()

            # Verificar existencia de la categoría padre
            cursor.execute("SELECT COUNT(*) FROM TablaCategorias WHERE nombre = %s", (categoria_padre,))
            result = cursor.fetchone()
            parent_exists = result is not None and result[0] > 0

            if not parent_exists:
                return {'ok': False, 'error': 'La categoría padre no existe.'}

            # Verificar si ya existe una fila con el mismo nombre y categoría padre
            cursor.execute("SELECT COUNT(*) FROM TablaCategorias WHERE nombre = %s AND categoria_padre = %s", (nombre, categoria_padre))
            result = cursor.fetchone()
            if result is not None and result[0] > 0:
                return {'ok': False, 'error': 'La categoría con este nombre y categoría padre ya existe.'}

            # Insertar la nueva categoría
            cursor.execute("INSERT INTO TablaCategorias (nombre, categoria_padre) VALUES (%s, %s)", (nombre, categoria_padre))
            conexion.commit()
            return {'ok': True, 'mensaje': 'Categoría agregada correctamente.'}
        except mysql.connector.Error as err:
            print(f"Error al agregar la categoría: {err}")
            return {'ok': False, 'error': str(err)}
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    @staticmethod
    def eliminar_categoria(data):
        """
        Elimina una categoría, reasigna contenidos y subcategorías a la categoría padre.
        Devuelve {'ok': True, 'mensaje': ...} o {'ok': False, 'error': ...}
        """
        nombre = data.get('nombre')
        categoria_padre = data.get('categoria_padre')

        if not nombre or not categoria_padre:
            return {'ok': False, 'error': 'Faltan parámetros'}

        if categoria_padre.upper() == "ROOT":
            return {'ok': False, 'error': 'No se puede eliminar una categoría ROOT.'}

        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()

            # Verificar si la categoría existe
            cursor.execute("SELECT COUNT(*) FROM TablaCategorias WHERE nombre = %s AND categoria_padre = %s", (nombre, categoria_padre))
            existe = cursor.fetchone()[0] > 0
            if not existe:
                return {'ok': False, 'error': f"La categoría '{nombre}' con padre '{categoria_padre}' no existe."}

            # Obtener la categoría padre de la categoría a eliminar
            cursor.execute("SELECT categoria_padre FROM TablaCategorias WHERE nombre = %s AND categoria_padre = %s", (nombre, categoria_padre))
            nueva_categoria = cursor.fetchone()
            cursor.fetchall()  # Limpiar resultados pendientes

            if nueva_categoria is None:
                return {'ok': False, 'error': f"No se pudo determinar la categoría padre de '{nombre}'."}
            nueva_categoria = nueva_categoria[0]

            # Reasignar contenidos a la categoría padre
            cursor.execute("UPDATE TablaContenidos SET categoria = %s WHERE categoria = %s", (nueva_categoria, nombre))
            conexion.commit()

            # Reasignar subcategorías a la nueva categoría padre
            cursor.execute("UPDATE TablaCategorias SET categoria_padre = %s WHERE categoria_padre = %s", (nueva_categoria, nombre))
            conexion.commit()

            # Eliminar la categoría
            cursor.execute("DELETE FROM TablaCategorias WHERE nombre = %s AND categoria_padre = %s", (nombre, categoria_padre))
            conexion.commit()

            return {'ok': True, 'mensaje': 'Categoría eliminada correctamente'}
        except mysql.connector.Error as err:
            print(f"Error al eliminar la categoría: {err}")
            return {'ok': False, 'error': str(err)}
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def editar_categoria(data):
        """Edita el nombre de una categoría y actualiza los contenidos relacionados."""
        nombre_actual = data.get('nombre_actual')
        nuevo_nombre = data.get('nuevo_nombre')

        if not nombre_actual or not nuevo_nombre:
            return {'ok': False, 'error': 'Faltan parámetros'}

        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            # Modificar el nombre de la categoría 
            cursor.execute("UPDATE TablaCategorias SET nombre = %s WHERE nombre = %s", (nuevo_nombre, nombre_actual))
            conexion.commit()
            # Modificar el nombre de la categoría en TablaContenidos
            cursor.execute("UPDATE TablaContenidos SET categoria = %s WHERE categoria = %s", (nuevo_nombre, nombre_actual))
            conexion.commit()
            return {'ok': True, 'mensaje': 'Categoría editada correctamente'}
        except mysql.connector.Error as err:
            print(f"Error al editar la categoría: {err}")
            return {'ok': False, 'error': str(err)}
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def verificar_categoria(nombre, padre):
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()
            # Verificar si la categoría existe
            cursor.execute("SELECT EXISTS(SELECT 1 FROM TablaCategorias WHERE nombre = %s AND categoria_padre = %s)", (nombre, padre))
            existe = cursor.fetchone()[0]

            if existe:
                print(f"La categoría '{nombre}' con padre '{padre}' ya existe.")
            else:
                print(f"La categoría '{nombre}' con padre '{padre}' no existe.")

            return existe
        except mysql.connector.Error as err:
            print(f"Error al verificar la categoría: {err}")
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def verificar_categoria_externa(nombre, padre):
        """Verifica si una categoría existe dado su nombre y padre."""
        if not nombre:
            return {'status': 400, 'data': {'error': "El parámetro 'nombre' es obligatorio."}}
        if not padre:
            return {'status': 200, 'data': {'existe': True}}
        existe = GestorCategorias.verificar_categoria(nombre, padre)
        return {'status': 200, 'data': {'existe': existe}}

    @staticmethod
    def obtener_categorias(filter_parent='', sort=False):
        """Devuelve una lista de categorías, opcionalmente filtradas por padre y ordenadas por nombre."""
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)
            sql = "SELECT * FROM TablaCategorias"
            params = []
            if filter_parent:
                sql += " WHERE categoria_padre = %s"
                params.append(filter_parent)
            if sort:
                sql += " ORDER BY nombre ASC"
            cursor.execute(sql, params)
            categorias = cursor.fetchall()
            return categorias
        except mysql.connector.Error as err:
            print(f"Error al obtener categorías: {err}")
            return []
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def obtener_categorias_hijas(padre):
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor(dictionary=True)
            # Obtener las categorías hijas de una categoría dada
            cursor.execute("SELECT nombre FROM TablaCategorias WHERE categoria_padre = %s", (padre,))
            categorias = cursor.fetchall()
            return categorias
        except Exception as e:
            print(f"[DEBUG] Error en obtener_categorias_hijas: {e}")
            return None
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()