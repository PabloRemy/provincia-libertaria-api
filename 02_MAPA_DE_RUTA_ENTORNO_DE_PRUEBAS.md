# Mapa de ruta — Entorno de pruebas

Última actualización: 28 de junio de 2026.

## Instrucción para futuras sesiones de Codex

Leer, en este orden:

1. `00_PROVINCIA_LIBERTARIA_MASTER.md`
2. `01_DESARROLLO_TECNICO.md`
3. Este documento.
4. `README_TESTS.md`

Antes de modificar archivos, comprobar el estado real del proyecto y ejecutar
la suite de pruebas. No tocar el VPS ni producción sin autorización expresa,
respaldo y un procedimiento de reversión.

## Objetivo

Construir en la computadora local una réplica segura y suficientemente fiel de
Provincia Libertaria para desarrollar y probar cambios antes de publicarlos en
el VPS.

El entorno local debe usar datos ficticios y recursos aislados. Nunca debe
conectarse accidentalmente a la base de datos productiva.

## Arquitectura prevista

### Entorno local

- FastAPI local.
- PostgreSQL de pruebas en Docker.
- Archivos subidos en un directorio temporal local.
- Usuarios y contraseñas ficticios.
- Pruebas automáticas y revisión visual en navegador.

### Producción

- WordPress como frontend.
- FastAPI como backend.
- PostgreSQL real.
- Docker, Coolify y VPS Hostinger.
- Datos y usuarios reales.

Los entornos deben permanecer separados.

## Estado actual

### Completado

- Entorno virtual Python `.venv`.
- Dependencias de desarrollo en `requirements-dev.txt`.
- Configuración de pytest en `pytest.ini`.
- Pruebas de página principal, normalización y ciudades.
- Pruebas de autenticación y permisos territoriales.
- Prueba de integración con PostgreSQL.
- Esquema descartable en `sql/test_schema.sql`.
- Docker Engine y Docker Compose instalados en la computadora.
- PostgreSQL 16 de pruebas definido en `compose.test.yml`.
- Puerto publicado sólo en `127.0.0.1:55432`.
- Base `provincia_libertaria_test` protegida mediante sufijo `_test`.
- Suite completa verificada: 25 pruebas aprobadas.

### Todavía no realizado

- No se probó la aplicación completa desde el navegador.
- No se comparó la copia local con la versión actualmente desplegada en el VPS.
- No existe todavía un procedimiento de publicación, respaldo y reversión.

## Comandos habituales

Ubicación del proyecto:

```bash
cd /home/lab/Documentos/provincialibertaria/provincia-libertaria-api
```

Levantar PostgreSQL de pruebas:

```bash
sudo docker compose -f compose.test.yml up -d --wait
```

Preparar las variables locales, si `.env.test` todavía no existe:

```bash
cp .env.test.example .env.test
```

Ejecutar todas las pruebas:

```bash
set -a
source .env.test
set +a
.venv/bin/pytest -q
```

Resultado validado al crear este documento:

```text
25 passed
```

Detener PostgreSQL conservando el volumen:

```bash
sudo docker compose -f compose.test.yml down
```

Detener PostgreSQL y eliminar todos sus datos descartables:

```bash
sudo docker compose -f compose.test.yml down -v
```

## Mapa de ruta

### Etapa 1 — Punto de restauración local (completada)

1. Revisar archivos sensibles y exclusiones de `.gitignore`.
2. Inicializar un repositorio Git local.
3. Registrar el estado inicial conocido y probado.
4. No publicar todavía el repositorio en ningún servicio externo.

Condición de finalización: existe un punto de restauración local y las 25
pruebas continúan aprobando.

### Etapa 2 — API local completa (completada)

1. Incorporar FastAPI a `compose.test.yml` o a una configuración local
   equivalente.
2. Conectar exclusivamente con `provincia_libertaria_test`.
3. Usar un directorio local temporal para las imágenes.
4. Agregar comprobaciones de salud para API y PostgreSQL.

Condición de finalización: la API responde localmente sin depender del VPS.

### Etapa 3 — Datos ficticios reproducibles (completada)

1. Crear registros de ejemplo para Berisso, Ensenada y La Plata.
2. Incluir categorías, barrios, estados y coordenadas representativas.
3. Crear usuarios administrativos ficticios con distintos alcances.
4. Automatizar la carga y limpieza de esos datos.

Condición de finalización: cualquier sesión puede reconstruir el mismo escenario
de prueba desde cero.

### Etapa 4 — Validación funcional

1. Probar formularios de reclutamiento y reportes. En progreso: validado un
   reporte sin barrio, foto ni GPS mediante el endpoint usado por CF7.
2. Probar autenticación y restricciones por distrito.
3. Probar carga y visualización de imágenes.
4. Probar paneles, mapas, filtros y moderación.
5. Agregar pruebas automáticas para los defectos encontrados.

Condición de finalización: los recorridos principales funcionan mediante API y
navegador, con evidencia reproducible.

### Etapa 5 — Comparación con producción

1. Identificar exactamente qué versión se ejecuta en el VPS.
2. Comparar configuración, esquema y código sin copiar secretos ni datos reales.
3. Registrar diferencias y migraciones necesarias.
4. Mantener producción en modo de sólo lectura durante este análisis.

Condición de finalización: se conocen las diferencias entre local y producción.

### Etapa 6 — Publicación segura

1. Crear respaldo verificable de base y archivos.
2. Definir migraciones y orden de despliegue.
3. Definir comprobaciones posteriores a la publicación.
4. Definir un procedimiento de reversión.
5. Publicar sólo con autorización expresa.

Condición de finalización: cambio desplegado, verificado y reversible.

## Próximo paso acordado

Comenzar la Etapa 4: validar sistemáticamente formularios, autenticación,
permisos, imágenes, paneles, mapas y moderación.

## Reglas de seguridad

- Nunca usar credenciales reales en `.env.test`.
- Nunca apuntar `TEST_DATABASE_URL` a producción.
- Toda base de integración debe terminar en `_test`.
- No subir archivos `.env` al control de versiones.
- No ejecutar migraciones ni despliegues en el VPS sin autorización expresa.
- Antes de publicar: pruebas aprobadas, respaldo y reversión definidos.
