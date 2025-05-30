CREATE TABLE proyecto.TablaContenido (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    autor VARCHAR(255) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) NOT NULL,
    extension VARCHAR(20),
    mime VARCHAR(100),
    precio DECIMAL(10,2) DEFAULT 0,
    calificacion DECIMAL(3,2) DEFAULT 0,
    archivo LONGBLOB
);

INSERT INTO proyecto.TablaContenido (nombre, autor, descripcion, tipo, extension, mime, precio, calificacion, archivo)
VALUES
('Canción de ejemplo', 'Juan Pérez', 'Una canción de prueba para el sistema.', 'audio', 'mp3', 'audio/mpeg', 5.00, 4.5, NULL),
('Imagen de portada', 'Ana Gómez', 'Imagen utilizada como portada principal.', 'imagen', 'jpg', 'image/jpeg', 2.50, 4.8, NULL),
('Video promocional', 'Carlos Ruiz', 'Video corto para promoción.', 'video', 'mp4', 'video/mp4', 10.00, 4.2, NULL);

SELECT nombre FROM TablaCategorias WHERE categoria_padre = 'video'