import mysql.connector
import decimal
from gestorConfig import DB_CONFIG

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