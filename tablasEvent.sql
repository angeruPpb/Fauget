-- Evento para que se eliminen las promociones vencidas
-- y se actualicen los contenidos relacionados
DELIMITER $$ 
CREATE EVENT IF NOT EXISTS limpiar_promociones_vencidas
ON SCHEDULE EVERY 1 DAY
DO
BEGIN
    UPDATE proyecto.TablaContenido c
    JOIN proyecto.TablaPromocion p ON c.promocion_id = p.id
    SET c.promocion_id = NULL
    WHERE p.fecha_fin < CURDATE();
END$$
DELIMITER ;

-- Aumentar el tamaño máximo de paquete permitido para manejar archivos grandes
SET GLOBAL max_allowed_packet = 104857600;

-- Desactiva promociones no vigentes
    UPDATE TablaPromocion
    SET estado = 0
    WHERE CURDATE() < fecha_inicio OR CURDATE() > fecha_fin;