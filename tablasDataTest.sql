
--- Administrador
INSERT INTO proyecto.TablaUsuarios (username_, password_)
VALUES ('admin', '1234');


-- Insertar categorías iniciales
INSERT INTO proyecto.TablaCategorias (nombre, categoria_padre) VALUES
('video', 'ROOT'),
('imagen', 'ROOT'),
('sonido', 'ROOT'),
('Películas', 'video'),
('Documentales', 'video'),
('Animación', 'video'),
('Fotografía de Naturaleza', 'imagen'),
('Retratos', 'imagen'),
('Paisajes', 'imagen'),
('Rock', 'sonido'),
('Clásica', 'sonido'),
('Jazz', 'sonido'),
('Películas de Acción', 'Películas'),
('Películas de Comedia', 'Películas'),
('Naturaleza Salvaje', 'Documentales'),
('Historia del Mundo', 'Documentales'),
('Animación 2D', 'Animación'),
('Animación 3D', 'Animación'),
('Aves', 'Fotografía de Naturaleza'),
('Bosques', 'Fotografía de Naturaleza'),
('Retratos en Blanco y Negro', 'Retratos'),
('Retratos de Estudio', 'Retratos'),
('Montañas', 'Paisajes'),
('Playas', 'Paisajes'),
('Rock Clásico', 'Rock'),
('Rock Alternativo', 'Rock'),
('Barroco', 'Clásica'),
('Romántico', 'Clásica'),
('Smooth Jazz', 'Jazz'),
('Jazz Bebop', 'Jazz');

-- agregar clientes 
INSERT INTO proyecto.TablaCliente (idAdmin, estado, nombre, correo, username, password, saldo, promoespecial) VALUES
(1, 'cliente', 'Ana Torres', 'ana@mail.com', 'ana', 'pass1', 100, FALSE),
(1, 'cliente', 'Luis Pérez', 'luis@mail.com', 'luis', 'pass2', 150, TRUE),
(1, 'cliente', 'Marta Díaz', 'marta@mail.com', 'marta', 'pass3', 200, FALSE),
(1, 'cliente', 'Carlos Ruiz', 'carlos@mail.com', 'carlos', 'pass4', 50, FALSE),
(1, 'cliente', 'Elena Gómez', 'elena@mail.com', 'elena', 'pass5', 80, TRUE),
(1, 'cliente', 'Pedro López', 'pedro@mail.com', 'pedro', 'pass6', 120, FALSE),
(1, 'cliente', 'Lucía Sánchez', 'lucia@mail.com', 'lucia', 'pass7', 90, FALSE),
(1, 'cliente', 'Javier Ramos', 'javier@mail.com', 'javier', 'pass8', 60, FALSE),
(1, 'cliente', 'Sofía Romero', 'sofia@mail.com', 'sofia', 'pass9', 110, TRUE),
(1, 'cliente', 'Diego Herrera', 'diego@mail.com', 'diego', 'pass10', 70, FALSE),
(1, 'cliente', 'jean','jean@example.com', 'jean', '1234', 2000, TRUE);

-- Insertar promociones iniciales
INSERT INTO proyecto.TablaPromocion (nombre, porcentaje, descripcion, fecha_inicio, fecha_fin) VALUES
('Promo Primavera', 10, 'Descuento de primavera', '2024-03-01', '2024-06-01'),
('Promo Verano', 15, 'Descuento de verano', '2024-06-02', '2024-09-01'),
('Promo Otoño', 20, 'Descuento de otoño', '2024-09-02', '2024-12-01'),
('Promo Invierno', 25, 'Descuento de invierno', '2024-12-02', '2025-03-01'),
('Promo Especial', 30, 'Descuento especial', '2024-01-01', '2025-01-01');

-- Insertar Notificaciones
INSERT INTO proyecto.Notificacion (usuario_id, emisor, mensaje)
SELECT id, 'Sistema', '¡Bienvenido a la plataforma!' FROM proyecto.TablaCliente;

-- Insertar contenidos iniciales
INSERT INTO proyecto.TablaContenido
(nombre, autor, categoria, descripcion, tipo, extension, mime, precio, calificacion, archivo, promocion_id)
VALUES
('Aventura en la Montaña', 'Ana Torres', 'Películas de Acción', 'Película de acción en la montaña', 'video', 'mp4', 'video/mp4', 120, 4.5, NULL, 1),
('Documental de Bosques', 'Luis Pérez', 'Bosques', 'Documental sobre bosques del mundo', 'video', 'mp4', 'video/mp4', 90, 4.2, NULL, 2),
('Animación 3D: Viaje Espacial', 'Marta Díaz', 'Animación 3D', 'Animación 3D de un viaje espacial', 'video', 'mp4', 'video/mp4', 80, 4.8, NULL, 3),
('Comedia Urbana', 'Carlos Ruiz', 'Películas de Comedia', 'Película de comedia en la ciudad', 'video', 'mp4', 'video/mp4', 70, 4.0, NULL, 4),
('Historia del Mundo Antiguo', 'Elena Gómez', 'Historia del Mundo', 'Documental sobre el mundo antiguo', 'video', 'mp4', 'video/mp4', 100, 4.6, NULL, 5),
('Paisaje de Montañas', 'Pedro López', 'Montañas', 'Fotografía de montañas al amanecer', 'imagen', 'jpg', 'image/jpeg', 30, 4.9, NULL, 1),
('Retrato de Estudio', 'Lucía Sánchez', 'Retratos de Estudio', 'Retrato profesional en estudio', 'imagen', 'jpg', 'image/jpeg', 25, 4.7, NULL, 2),
('Naturaleza Salvaje: Aves', 'Javier Ramos', 'Aves', 'Fotografía de aves en su hábitat', 'imagen', 'jpg', 'image/jpeg', 35, 4.8, NULL, 3),
('Playa Tropical', 'Sofía Romero', 'Playas', 'Fotografía de una playa tropical', 'imagen', 'jpg', 'image/jpeg', 28, 4.5, NULL, 4),
('Retrato en Blanco y Negro', 'Diego Herrera', 'Retratos en Blanco y Negro', 'Retrato artístico en blanco y negro', 'imagen', 'jpg', 'image/jpeg', 22, 4.3, NULL, 5),
('Rock Clásico: Solo de Guitarra', 'Ana Torres', 'Rock Clásico', 'Solo de guitarra de rock clásico', 'sonido', 'mp3', 'audio/mpeg', 15, 4.6, NULL, 1),
('Jazz Bebop Improvisación', 'Luis Pérez', 'Jazz Bebop', 'Improvisación de jazz bebop', 'sonido', 'mp3', 'audio/mpeg', 18, 4.4, NULL, 2),
('Barroco para Piano', 'Marta Díaz', 'Barroco', 'Pieza barroca interpretada en piano', 'sonido', 'mp3', 'audio/mpeg', 20, 4.7, NULL, 3),
('Rock Alternativo: Nueva Era', 'Carlos Ruiz', 'Rock Alternativo', 'Canción de rock alternativo', 'sonido', 'mp3', 'audio/mpeg', 17, 4.2, NULL, 4),
('Smooth Jazz Nocturno', 'Elena Gómez', 'Smooth Jazz', 'Pieza de smooth jazz para la noche', 'sonido', 'mp3', 'audio/mpeg', 19, 4.9, NULL, 5);

-- Relacionar los 15 contenidos con los 10 clientes, 3 por cliente (puedes ajustar los IDs según tus inserts)
INSERT INTO proyecto.ContenidoCliente (usuario_id, contenido_id) VALUES
(1, 1), (1, 2), (1, 3),
(2, 4), (2, 5), (2, 6),
(3, 7), (3, 8), (3, 9),
(4, 10), (4, 11), (4, 12),
(5, 13), (5, 14), (5, 15),
(6, 1), (6, 4), (6, 7),
(7, 2), (7, 5), (7, 8),
(8, 3), (8, 6), (8, 9),
(9, 10), (9, 13), (9, 14),
(10, 11), (10, 12), (10, 15);

SELECT * FROM TablaCliente WHERE username = 'jean';