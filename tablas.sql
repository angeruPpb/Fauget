
SHOW DATABASES;

CREATE DATABASE proyecto
    DEFAULT CHARACTER SET = 'utf8mb4'
    COLLATE = 'utf8mb4_general_ci';


-- crear tabla de usuarios
CREATE TABLE proyecto.TablaUsuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username_ VARCHAR(255) NOT NULL,
    password_ VARCHAR(255) NOT NULL
);

-- Crear tabla de categorías
CREATE TABLE proyecto.TablaCategorias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    categoria_padre VARCHAR(255) DEFAULT NULL,
    estado TINYINT(1) DEFAULT 1
);

-- Crear tabla de promociones
CREATE TABLE proyecto.TablaPromocion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    porcentaje DECIMAL(5,2) NOT NULL,
    descripcion VARCHAR(255),
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE NOT NULL,
    estado TINYINT(1) DEFAULT 1
);

-- Crear tabla de contenidos
CREATE TABLE proyecto.TablaContenido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    autor VARCHAR(255) NOT NULL,
    categoria VARCHAR(255),
    descripcion TEXT,
    tipo VARCHAR(50) NOT NULL,
    extension VARCHAR(20),
    mime VARCHAR(100),
    precio DECIMAL(10,2) DEFAULT 0,
    calificacion DECIMAL(3,2) DEFAULT 0,
    archivo LONGBLOB,
    promocion_id INT DEFAULT NULL,
    estado TINYINT(1) DEFAULT 1,
    FOREIGN KEY (promocion_id) REFERENCES proyecto.TablaPromocion(id) ON DELETE SET NULL
);

-- Crear tabla de usuarios
CREATE TABLE proyecto.TablaCliente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    idAdmin INT NOT NULL,
    estado ENUM('cliente', 'excliente') NOT NULL,
    nombre VARCHAR(255) NOT NULL,
    correo VARCHAR(255) NOT NULL UNIQUE,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    saldo DECIMAL(10,2) DEFAULT 0,
    promoespecial BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (idAdmin) REFERENCES proyecto.TablaUsuarios(id)
);

-- Relación de contenidos adquiridos por usuario
CREATE TABLE proyecto.ContenidoCliente (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    contenido_id INT NOT NULL,
    fecha_adquirido DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES proyecto.TablaCliente(id) ON DELETE CASCADE,
    FOREIGN KEY (contenido_id) REFERENCES proyecto.TablaContenido(id) ON DELETE CASCADE
);

-- Tabla de notificaciones para usuarios
CREATE TABLE proyecto.Notificacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    emisor VARCHAR(255) NOT NULL,
    mensaje TEXT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES proyecto.TablaCliente(id) ON DELETE CASCADE
);

