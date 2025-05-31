# gestorPerfil.py

import mysql.connector
import decimal
from gestorConfig import DB_CONFIG

def obtener_perfil(id_cliente):
    """
    Retorna un diccionario con los datos del cliente identificado por id_cliente.
    Campos devueltos: idCliente, nombre, correo, saldo (float), foto.
    """
    conexion = mysql.connector.connect(**DB_CONFIG)
    cursor = conexion.cursor(dictionary=True)
    try:
        consulta = "SELECT id, nombre, correo, username, saldo FROM TablaCliente WHERE id = %s"
        cursor.execute(consulta, (id_cliente,))
        resultado = cursor.fetchone()
        if resultado:
            # Convertir saldo Decimal a float
            resultado['saldo'] = float(resultado['saldo']) if isinstance(resultado['saldo'], decimal.Decimal) else resultado['saldo']
            return resultado
        else:
            return None
    finally:
        cursor.close()
        conexion.close()

def editar_perfil(id_cliente, nuevo_nombre, nuevo_correo, contrasena_anterior, nueva_contrasena=None, ruta_foto=None):
    """
    Valida que la contrasena_anterior sea correcta y, de serlo, actualiza
    los campos nombre, correo, contrasena y/o foto para el cliente dado.
    Retorna tupla (exito, mensaje). exito = True/False, mensaje con texto descriptivo.
    """
    conexion = mysql.connector.connect(**DB_CONFIG)
    cursor = conexion.cursor()
    try:
        # 1) Verificar que contrasena_anterior coincida con la actual en BD
        consulta_pass = "SELECT password FROM TablaCliente WHERE id = %s"
        cursor.execute(consulta_pass, (id_cliente,))
        resultado = cursor.fetchone()
        if not resultado:
            return (False, "Cliente no encontrado.")
        password_actual = resultado[0]

        # OJO: aqui asumimos que la contraseña en BD esta guardada en texto plano o con algun hash simple.
        # Si usas hashing, aqui habria que comparar hash(contrasena_anterior) vs password_actual.
        if contrasena_anterior != password_actual:
            return (False, "La contrasena anterior no coincide.")

        # 2) Armar la sentencia UPDATE dinamicamente
        campos = []
        valores = []

        # Nombre y correo siempre deben cambiarse (se validan arriba en la capa de servidor antes de llamar).
        campos.append("nombre = %s")
        valores.append(nuevo_nombre)

        campos.append("correo = %s")
        valores.append(nuevo_correo)

        # Si se proporciono nueva_contrasena y no es cadena vacia, actualizar contraseña
        if nueva_contrasena:
            campos.append("password = %s")
            valores.append(nueva_contrasena)

        # Si se proporciono ruta_foto, actualizar
        if ruta_foto:
            campos.append("foto = %s")
            valores.append(ruta_foto)

        # Construir la parte final de la consulta
        if not campos:
            return (False, "No hay campos para actualizar.")
        valores.append(id_cliente)
        sql_update = "UPDATE TablaCliente SET " + ", ".join(campos) + " WHERE id = %s"

        cursor.execute(sql_update, tuple(valores))
        conexion.commit()

        if cursor.rowcount > 0:
            return (True, "Perfil actualizado exitosamente.")
        else:
            return (False, "No se actualizo ningun campo. Verifica los datos.")
    except mysql.connector.Error as err:
        return (False, f"Error en la base de datos: {err}")
    finally:
        cursor.close()
        conexion.close()
