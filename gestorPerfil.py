# gestorPerfil.py

import mysql.connector
import decimal
from gestorConfig import DB_CONFIG

'''
Gestor Perfil (OG12)
Funciones:
- (FA026) obtener_perfil: Recupera los datos básicos del cliente (id, nombre, correo, username, saldo).
- (FA027) editar_perfil: Valida la contraseña anterior y actualiza nombre, correo, contraseña y/o foto del cliente.
- (FA028) obtener_notas: Obtiene la lista de calificaciones (notas) del cliente desde su historial.
- (FA029) obtener_historial: Recupera los últimos registros de descargas/compras realizadas por el cliente.
'''

def obtener_perfil(id_cliente):  # FA026
    """
    Retorna un diccionario con los datos del cliente identificado por id_cliente.
    Campos devueltos: id (int), nombre (str), correo (str), username (str), saldo (float).
    """
    # 1) Abrir conexion a la base de datos
    conexion = mysql.connector.connect(**DB_CONFIG)
    cursor = conexion.cursor(dictionary=True)
    try:
        # 2) Definir y ejecutar consulta para obtener perfil
        consulta = "SELECT id, nombre, correo, username, saldo FROM TablaCliente WHERE id = %s"
        cursor.execute(consulta, (id_cliente,))
        resultado = cursor.fetchone()
        if resultado:
            # 3) Convertir saldo de Decimal a float para facilitar manejo en capa de presentación
            if isinstance(resultado['saldo'], decimal.Decimal):
                resultado['saldo'] = float(resultado['saldo'])
            return resultado
        else:
            # 4) Si no existe registro para ese id, devolver None
            return None
    finally:
        # 5) Cerrar recursos (cursor y conexion) siempre, incluso ante excepciones
        cursor.close()
        conexion.close()


def editar_perfil(id_cliente, nuevo_nombre, nuevo_correo, contrasena_anterior, nueva_contrasena=None, ruta_foto=None):  # FA027
    """
    Valida que contrasena_anterior coincida con la almacenada en BD.
    Si coincide, actualiza nombre, correo y opcionalmente contraseña y/o ruta de foto.
    Retorna tupla (exito: bool, mensaje: str).
    """
    # 1) Abrir conexion a la base de datos
    conexion = mysql.connector.connect(**DB_CONFIG)
    cursor = conexion.cursor()
    try:
        # 2) Recuperar la contraseña actual almacenada en BD para verificar
        consulta_pass = "SELECT password FROM TablaCliente WHERE id = %s"
        cursor.execute(consulta_pass, (id_cliente,))
        resultado = cursor.fetchone()
        if not resultado:
            # 3) Si no existe cliente con ese id, retornar error
            return (False, "Cliente no encontrado.")
        password_actual = resultado[0]

        # 4) Comparar contrasena_anterior ingresada con la almacenada (texto plano o hash simple)
        #    Si hay hashing, aquí se haría hash(contrasena_anterior) y se compararía con password_actual.
        if contrasena_anterior != password_actual:
            return (False, "La contrasena anterior no coincide.")

        # 5) Construir dinámicamente la lista de campos a actualizar
        campos = []
        valores = []

        # 5.1) Nombre siempre se actualiza
        campos.append("nombre = %s")
        valores.append(nuevo_nombre)

        # 5.2) Correo siempre se actualiza
        campos.append("correo = %s")
        valores.append(nuevo_correo)

        # 5.3) Si se proporcionó nueva_contrasena, actualizar contraseña
        if nueva_contrasena:
            campos.append("password = %s")
            valores.append(nueva_contrasena)

        # 5.4) Si se proporcionó ruta_foto, actualizar foto
        if ruta_foto:
            campos.append("foto = %s")
            valores.append(ruta_foto)

        # 6) Si no hay campos para actualizar, regresar error
        if not campos:
            return (False, "No hay campos para actualizar.")

        # 7) Agregar id_cliente al final de valores para la cláusula WHERE
        valores.append(id_cliente)
        # 8) Construir la sentencia UPDATE concatenando los campos
        sql_update = "UPDATE TablaCliente SET " + ", ".join(campos) + " WHERE id = %s"

        # 9) Ejecutar actualización
        cursor.execute(sql_update, tuple(valores))
        conexion.commit()

        # 10) Verificar si se afectó alguna fila: si rowcount > 0, hubo actualización
        if cursor.rowcount > 0:
            return (True, "Perfil actualizado exitosamente.")
        else:
            # 11) Si rowcount == 0, no se actualizó nada (quizás los mismos datos)
            return (False, "No se actualizo ningun campo. Verifica los datos.")
    except mysql.connector.Error as err:
        # 12) Controlar posibles errores de BD y retornarlos
        return (False, f"Error en la base de datos: {err}")
    finally:
        # 13) Cerrar recursos
        cursor.close()
        conexion.close()


def obtener_notas(id_cliente):  # FA028
    """
    Retorna una lista de notas (calificaciones) del cliente identificado por id_cliente.
    Cada elemento de la lista es un diccionario con: tipo (str), nombre (str), nota (float), fecha (ISO string).
    """
    # 1) Abrir conexion a la base de datos
    conexion = mysql.connector.connect(**DB_CONFIG)
    cursor = conexion.cursor(dictionary=True)
    try:
        # 2) Ejecutar consulta para obtener historial de notas/ calificaciones
        consulta = "SELECT tipo, nombre, nota, fecha FROM TablaHistorialCliente WHERE idCliente = %s"
        cursor.execute(consulta, (id_cliente,))
        resultados = cursor.fetchall()

        notas = []
        for fila in resultados:
            # 3) Convertir campo 'nota' de Decimal a float si corresponde
            if isinstance(fila.get('nota'), decimal.Decimal):
                fila['nota'] = float(fila['nota'])
            # 4) Convertir fecha a ISO string (YYYY-MM-DD o YYYY-MM-DDTHH:MM:SS)
            fecha_val = fila.get('fecha')
            if hasattr(fecha_val, 'isoformat'):
                fila['fecha'] = fecha_val.isoformat()
            notas.append(fila)

        return notas
    finally:
        # 5) Cerrar recursos
        cursor.close()
        conexion.close()


def obtener_historial(id_cliente, limit=10):  # FA029
    """
    Retorna los ultimos registros de descargas/compras para el cliente.
    Cada registro es un diccionario con: tipo (str), nombre (str), beneficiario (str), fecha (ISO string).
    El parámetro 'limit' define cuántos registros recientes retornar (por defecto 10).
    """
    # 1) Abrir conexion a la base de datos
    conexion = mysql.connector.connect(**DB_CONFIG)
    cursor = conexion.cursor(dictionary=True)
    try:
        # 2) Consulta que une tabla Compra con TablaContenido para obtener detalles de cada descarga/compra
        consulta = (
            "SELECT c.tipo, cont.nombre, c.beneficiario, c.fecha "
            "FROM Compra c "
            "JOIN TablaContenido cont ON c.idHistorial = cont.id "
            "WHERE c.idCliente = %s "
            "ORDER BY c.fecha DESC LIMIT %s"
        )
        cursor.execute(consulta, (id_cliente, limit))
        resultados = cursor.fetchall()

        historial = []
        for fila in resultados:
            # 3) Convertir fecha a ISO string
            fecha_val = fila.get('fecha')
            if hasattr(fecha_val, 'isoformat'):
                fila['fecha'] = fecha_val.isoformat()
            historial.append(fila)

        return historial
    finally:
        # 4) Cerrar recursos
        cursor.close()
        conexion.close()