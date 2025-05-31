import mysql.connector
from gestorConfig import DB_CONFIG
'''
Objeto gestor categorias OG18 modifica la tabla categorias OE14 y la tabla contenidos OE07
'''
class GestorCategorias: 
    @staticmethod
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
            print(f"Error al agregar la categoría: {err}")
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def eliminar_categoria(data):
        nombre = data.get('nombre')
        categoria_padre = data.get('categoria_padre')

        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()

            # Verificar si la categoría existe
            print(f"Depuración: Verificando si la categoría '{nombre}' con padre '{categoria_padre}' existe.")
            cursor.execute("SELECT COUNT(*) FROM TablaCategorias WHERE nombre = %s AND categoria_padre = %s", (nombre, categoria_padre))
            existe = cursor.fetchone()[0] > 0
            print(f"Depuración: Resultado de existencia: {existe}")

            if not existe:
                print(f"La categoría '{nombre}' con padre '{categoria_padre}' no existe.")
                return False

            # Obtener la categoría padre de la categoría eliminada
            print(f"Depuración: Obteniendo la categoría padre de '{nombre}'.")
            cursor.execute("SELECT categoria_padre FROM TablaCategorias WHERE nombre = %s AND categoria_padre = %s", (nombre, categoria_padre))
            nueva_categoria = cursor.fetchone()
            cursor.fetchall()  # Limpia cualquier resultado pendiente
            print(f"Depuración: Resultado de la categoría padre: {nueva_categoria}")

            if nueva_categoria is None:
                print(f"No se pudo determinar la categoría padre de '{nombre}'.")
                return False
            nueva_categoria = nueva_categoria[0]

            # Actualizar los contenidos relacionados en TablaContenidos
            print(f"Depuración: Actualizando los contenidos relacionados en TablaContenidos.")
            # cursor.execute("UPDATE tablacontenidos SET categoria = %s WHERE categoria = %s", (nueva_categoria, nombre))
            # conexion.commit()
            print(f"Depuración: Contenidos actualizados correctamente.")

            # Actualizar los contenidos relacionados en TablaCategorias
            print(f"Depuración: Actualizando los contenidos relacionados en TablaCategorias.")
            cursor.execute("UPDATE TablaCategorias SET categoria_padre = %s WHERE categoria_padre = %s", (nueva_categoria, nombre))
            conexion.commit()
            print(f"Depuración: Categorias actualizados correctamente.")

            # Eliminar la categoría
            print(f"Depuración: Eliminando la categoría '{nombre}' con padre '{categoria_padre}'.")
            cursor.execute("DELETE FROM TablaCategorias WHERE nombre = %s AND categoria_padre = %s", (nombre, categoria_padre))
            conexion.commit()
            print(f"Depuración: Categoría eliminada correctamente.")

            print(f"Categoría '{nombre}' con padre '{categoria_padre}' eliminada correctamente.")
            print(f"Todos los contenidos relacionados fueron reasignados a la categoría '{nueva_categoria}'.")
            return True
        except mysql.connector.Error as err:
            print(f"Error al eliminar la categoría: {err}")
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def editar_categoria(data):
        nombre_actual = data.get('nombre_actual')
        nuevo_nombre = data.get('nuevo_nombre')

        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()

            # Actualizar el nombre de la categoría
            cursor.execute("UPDATE TablaCategorias SET nombre = %s WHERE nombre = %s", (nuevo_nombre, nombre_actual))
            conexion.commit()

            # Actualizar los contenidos relacionados en TablaContenidos
            # cursor.execute("UPDATE tablacontenidos SET categoria = %s WHERE categoria = %s", (nuevo_nombre, nombre_actual))
            # conexion.commit()

            print(f"Categoría '{nombre_actual}' actualizada a '{nuevo_nombre}' en TablaCategorias y TablaContenidos.")

            return True
        except mysql.connector.Error as err:
            print(f"Error al editar la categoría: {err}")
            return False
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conexion' in locals(): conexion.close()

    @staticmethod
    def verificar_categoria(nombre, padre):
        try:
            conexion = mysql.connector.connect(**DB_CONFIG)
            cursor = conexion.cursor()
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



def verificar_categoria_externa(nombre, padre):
    """Función externa para verificar si una categoría existe dado su nombre y padre."""
    if not nombre:
        return {'status': 400, 'data': {'error': "El parámetro 'nombre' es obligatorio."}}
    if not padre:
        return {'status': 200, 'data': {'existe': True}}
    existe = GestorCategorias.verificar_categoria(nombre, padre)
    return {'status': 200, 'data': {'existe': existe}}


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
