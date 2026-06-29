\ir test_schema.sql

BEGIN;

TRUNCATE TABLE incidentes, reclutamiento_registros RESTART IDENTITY;

INSERT INTO incidentes
    (ciudad, barrio, categoria, categoria_detalle, descripcion, direccion,
     estado, origen, fuente, latitud, longitud)
VALUES
    ('Berisso', 'Centro', 'Alumbrado', 'Luminaria apagada',
     'Reporte ficticio: luminaria sin funcionar.', 'Montevideo 450',
     'pendiente', 'vecino', 'datos-prueba', -34.8722, -57.8834),
    ('Berisso', 'Villa Progreso', 'Calles', 'Bache',
     'Reporte ficticio: bache sobre la calzada.', 'Calle 18 1250',
     'publicado', 'vecino', 'datos-prueba', -34.8890, -57.9001),
    ('Berisso', 'Los Talas', 'Residuos', 'Microbasural',
     'Reporte ficticio: residuos acumulados.', 'Avenida 66 3100',
     'resuelto', 'referente', 'datos-prueba', -34.9255, -57.8870),
    ('Ensenada', 'Centro', 'Seguridad', 'Zona oscura',
     'Reporte ficticio: sector con iluminación insuficiente.', 'La Merced 220',
     'pendiente', 'vecino', 'datos-prueba', -34.8617, -57.9106),
    ('Ensenada', 'El Dique', 'Calles', 'Desagüe obstruido',
     'Reporte ficticio: acumulación de agua luego de la lluvia.', 'Calle 126 680',
     'publicado', 'vecino', 'datos-prueba', -34.9030, -57.9450),
    ('Ensenada', 'Punta Lara', 'Ambiente', 'Costa',
     'Reporte ficticio: limpieza necesaria en espacio costero.', 'Almirante Brown 100',
     'oculto', 'referente', 'datos-prueba', -34.8121, -57.9800),
    ('La Plata', 'Casco Urbano', 'Tránsito', 'Semáforo',
     'Reporte ficticio: semáforo intermitente.', 'Calle 7 y 50',
     'pendiente', 'vecino', 'datos-prueba', -34.9214, -57.9544),
    ('La Plata', 'Tolosa', 'Calles', 'Bache',
     'Reporte ficticio: deterioro de pavimento.', 'Calle 528 900',
     'publicado', 'vecino', 'datos-prueba', -34.8975, -57.9815),
    ('La Plata', 'Los Hornos', 'Residuos', 'Recolección',
     'Reporte ficticio: demora en la recolección.', 'Calle 66 2100',
     'resuelto', 'referente', 'datos-prueba', -34.9780, -57.9850);

INSERT INTO reclutamiento_registros
    (nombre_apellido, whatsapp, email, ciudad, barrio, participacion, mensaje)
VALUES
    ('Persona Prueba Berisso', '0000000001', 'berisso@example.test',
     'Berisso', 'Centro', 'Referente barrial', 'Registro ficticio automatizado.'),
    ('Persona Prueba Ensenada', '0000000002', 'ensenada@example.test',
     'Ensenada', 'El Dique', 'Fiscalización', 'Registro ficticio automatizado.'),
    ('Persona Prueba La Plata', '0000000003', 'laplata@example.test',
     'La Plata', 'Tolosa', 'Comunicación', 'Registro ficticio automatizado.');

COMMIT;
