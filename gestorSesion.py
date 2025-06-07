# gestorSesion.py

import uuid
from http.cookies import SimpleCookie

'''
Gestor de Sesión (OG13)
Funciones:
- (FA030) crear_sesion: Genera un nuevo session_id, lo almacena en memoria y retorna el identificador.
- (FA031) obtener_cliente: Extrae session_id de la cabecera Cookie y devuelve el dict del cliente asociado.
- (FA032) obtener_cliente_sesion: Obtiene el cliente de la sesión o redirige si no existe.
'''

# Almacén de sesiones en memoria: session_id -> cliente dict
SESSIONS = {}

def crear_sesion(cliente):  # FA030
    """
    Genera y almacena un nuevo session_id para el cliente indicado.
    Parámetros:
    - cliente: diccionario con información del cliente que inicia sesión.
    Retorna:
    - sid (str): identificador de sesión generado (hexadecimal).
    """
    # 1) Generar un UUID único en formato hexadecimal para usar como session_id
    sid = uuid.uuid4().hex
    # 2) Almacenar en el diccionario en memoria la asociación session_id -> cliente
    SESSIONS[sid] = cliente
    # 3) Devolver el session_id para que se guarde en la cookie
    return sid

def obtener_cliente(cookie_header):  # FA031
    """
    Extrae el session_id de la cabecera Cookie y devuelve el cliente asociado.
    Parámetros:
    - cookie_header (str): contenido completo de la cabecera 'Cookie' HTTP.
    Retorna:
    - cliente (dict) o None si no existe sesión válida.
    """
    # 1) Parsear la cabecera de cookies usando SimpleCookie
    cookie = SimpleCookie(cookie_header)
    # 2) Obtener el valor de 'session_id' si existe; de lo contrario, sid será None
    sid = cookie.get('session_id') and cookie['session_id'].value
    # 3) Retornar el diccionario del cliente si el sid existe en SESSIONS; sino, None
    return SESSIONS.get(sid)

def obtener_cliente_sesion(headers, redirect_fn):  # FA032
    """
    Extrae el cliente de la sesión a partir de los encabezados HTTP.
    Si no hay cliente asociado, ejecuta la función de redirección y retorna None.
    Parámetros:
    - headers (dict): diccionario con encabezados HTTP de la petición.
    - redirect_fn (callable): función que recibe una URL y realiza la redirección.
    Retorna:
    - cliente (dict) si la sesión es válida; None si no existe sesión y se redirige.
    """
    # 1) Extraer la cabecera 'Cookie' si existe; de lo contrario, usar cadena vacía
    raw = headers.get('Cookie', '')
    # 2) Intentar obtener el cliente asociado a la sesión usando la función anterior
    cliente = obtener_cliente(raw)
    # 3) Si no se encuentra cliente (sesión inválida o inexistente), redirigir al login ('/')
    if not cliente:
        redirect_fn('/')
        return None
    # 4) Retornar el diccionario del cliente si la sesión es válida
    return cliente