# **Fauget**

Este proyecto es un sistema de compra y descarga de contenidos digitales desarrollado en Python utilizando un servidor HTTP básico y una base de datos MySQL. Permite agregar, editar y eliminar categorías, así como gestionar contenido relacionado -> Fauget V2.0

---

## **Requisitos previos**

Antes de ejecutar el programa, asegúrate de tener instalados los siguientes componentes:

1. **Python 3.10 o superior**  
   Descárgalo desde [python.org](https://www.python.org/).

2. **MySQL Server**  
   Puedes instalarlo a través de [XAMPP](https://www.apachefriends.org/) o directamente desde [MySQL](https://dev.mysql.com/downloads/).

3. **Pip** (Administrador de paquetes de Python)  
   Viene preinstalado con Python. Verifica su instalación ejecutando:
   ```bash
   pip --version
   ```

4. **Instalar los paquetes necesarios**  
   Asegúrate de instalar las dependencias listadas en el archivo `requirements.txt`.

---

## **Instalación**

### **1. Clonar el repositorio**
Clona este repositorio en tu máquina local:
```bash
git clone https://github.com/angeruPpb/Fauget.git
cd Fauget
```

### **2. Crear un entorno virtual**
Crea un entorno virtual para instalar las dependencias:
```bash
python -m venv venv
```

Activa el entorno virtual:
- **Windows:**
  ```bash
  venv\Scripts\activate
  ```
- **Linux/Mac:**
  ```bash
  source venv/bin/activate
  ```

### **3. Instalar las dependencias**
Instala los paquetes necesarios desde el archivo `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## **Configuración de la base de datos**

1. **Inicia MySQL Server**  
   Si usas XAMPP, asegúrate de que el servicio MySQL esté en ejecución.

2. **Crear la base de datos y tablas**  
   Ejecuta los siguientes scripts SQL en tu servidor MySQL para crear la base de datos y las tablas necesarias:

   - `tablas.sql`
   - `tablasdatatest.sql`

3. **Configurar la conexión a la base de datos**  
   Asegúrate de que las credenciales de conexión en el archivo `server.py` sean correctas:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': '',  # Cambia esto si tienes una contraseña configurada
       'database': 'proyecto'
   }
   ```

---

## **Ejecución del programa**

1. **Inicia el servidor**
   Ejecuta el archivo `server.py` para iniciar el servidor:
   ```bash
   python server.py
   ```

2. **Accede a la aplicación**
   Abre tu navegador y ve a:
   ```
   http://localhost:8000
   ```

3. **Funciones disponibles**
   - **Inicio de sesión:** Usa las credenciales `admin` y `1234` para acceder.
   - **Gestión de categorías:** Agregar, editar y eliminar categorías.
   - **Gestión de contenido:** Navega por las opciones disponibles en la interfaz.
   - **Gestión de promociones:** Crear, editar, activar/desactivar y eliminar promociones.
   - **Gestión de perfil:** Los clientes pueden ver y editar la información de su cuenta.
---

## **Notas importantes**

1. **Errores comunes:**
   - Si obtienes un error de conexión a MySQL, verifica que el servidor esté en ejecución y que las credenciales sean correctas.

---

## **Licencia**
Aun en desarrollo...

---
