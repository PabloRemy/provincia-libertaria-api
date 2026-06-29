CREATE TABLE IF NOT EXISTS incidentes (
    id BIGSERIAL PRIMARY KEY,
    ciudad TEXT NOT NULL,
    barrio TEXT NOT NULL,
    categoria TEXT NOT NULL,
    categoria_detalle TEXT,
    descripcion TEXT NOT NULL,
    direccion TEXT,
    foto_url TEXT,
    estado TEXT NOT NULL DEFAULT 'pendiente',
    origen TEXT DEFAULT 'vecino',
    fuente TEXT DEFAULT 'formulario',
    latitud DOUBLE PRECISION,
    longitud DOUBLE PRECISION,
    fecha_reporte TIMESTAMP NOT NULL DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reclutamiento_registros (
    id BIGSERIAL PRIMARY KEY,
    nombre_apellido TEXT NOT NULL,
    whatsapp TEXT NOT NULL,
    email TEXT,
    ciudad TEXT NOT NULL,
    barrio TEXT,
    participacion TEXT NOT NULL,
    mensaje TEXT,
    fecha_registro TIMESTAMP NOT NULL DEFAULT NOW()
);
