# Continuar desde aquí

## Bloque local sin publicar — 2026-10-03

La rama `integracion-local-sobre-github` incorpora un
login web con sesiones, logout y las mismas reglas de `ADMIN_USERS` y scopes.
El bloque inicial de login pasó 71 pruebas y una advertencia. No hubo push ni
despliegue. El entorno de pruebas necesita `SESSION_SECRET_KEY`
aleatorio y `DATA_DIR` escribible; ver `README_TESTS.md`. La información
fechada 2026-08-01 más abajo describe la línea base previa.

Pablo aprobó la validación manual y visual local: formulario `/login`,
autenticación de `admin-test` con scope `todos` y redirección de
`berisso-test` al panel de Berisso. Producción permaneció intacta. Al cierre,
el servidor de prueba seguía escuchando en `127.0.0.1:8001`; comprobar su
estado al retomar, sin asumir que seguirá activo.

Continuación de UX local: las vistas de Tercera Sección, distrito y edición
muestran usuario, scope legible y el botón `Salir` por POST a `/logout`. La
suite completa pasó con 74 pruebas y una advertencia; el logout y los permisos
territoriales siguen verificados. Pablo aprobó visualmente la nueva barra, el
logout y el reingreso con otro usuario. No se modificó producción.

Para continuar: verificar el estado Git y el commit local de este bloque. No
publicar ni preparar despliegue sin una etapa separada de revisión y
autorización.

Actualizado: 2026-08-01.

## Punto de partida verificado

- Repositorio: `https://github.com/PabloRemy/provincia-libertaria-api.git`.
- Clon local: `/home/desk/Documentos/Proyectos/provincia-libertaria-api`.
- Rama activa de desarrollo: `integracion-local-sobre-github`.
- Commit de partida de la validación local: `2a8b556`.
- La rama local coincidía con `origin/integracion-local-sobre-github` y el árbol
  estaba limpio antes y después de las validaciones.
- Rama productiva: `main`; `origin/main` permanece en `abc9807`.
- El contrato OpenAPI público y la etiqueta de la imagen productiva confirman
  `origin/main` (`abc9807bba2974ecd1bab36aa80166de3c66fbdf`).
- Existe un acceso SSH restringido mediante el alias local
  `provincia-vps-auditoria`; sólo ejecuta un informe fijo sin secretos.
- Antes de usar acceso SSH como `root` al VPS se debe obtener autorización
  expresa de Pablo; por defecto utilizar `provincia-vps-auditoria`.

## Decisión de sincronización

`main` e `integracion-local-sobre-github` tienen historiales independientes y
no poseen ancestro común. No ejecutar `pull`, merge ni rebase automático entre
ellas. `main` conserva la referencia productiva e histórica;
`integracion-local-sobre-github` es la fuente de verdad técnica para desarrollo.

La sincronización futura debe ser manual, revisada y controlada.

## Estado de trabajo confirmado

- Linux Mint 22.3 Zena sobre Ubuntu Noble `amd64`, Python 3.12.3 y `.venv`
  operativos. Docker Engine y Docker Compose instalados y comprobados.
- Suite sin PostgreSQL: 30 aprobadas, 1 deseleccionada y 1 advertencia. Suite
  completa con `TEST_DATABASE_URL`: 31 aprobadas y 1 advertencia.
- La `StarletteDeprecationWarning` por Starlette/httpx es una mejora técnica no
  bloqueante.
- `postgres-test`, `api-test`, `mysql-wordpress-test` y `wordpress-test`
  alcanzaron estado `healthy`.
- FastAPI, `/docs`, `/openapi.json`, WordPress, paneles territoriales, tablero,
  marcadores ficticios y autenticación administrativa fueron validados.
- La base aislada `provincia_libertaria_test` recibió 9 incidentes y 3 registros
  ficticios de reclutamiento.
- WordPress y CF7 fueron validados con y sin foto mediante el mu-plugin local,
  sin plugin externo de webhooks ni envío de correo.
- La carga CF7 con foto funciona extremo a extremo en local: el incidente 11,
  `foto_url`, archivo WebP, ruta `/foto/...` y panel de Berisso fueron
  verificados visualmente.
- La persistencia de WordPress, PostgreSQL y el WebP se conservó después de
  `docker compose down` sin `-v` y un nuevo arranque.
- Producción permaneció intacta. No se comparó todavía la rama de integración
  con el código y la configuración efectivamente desplegados.

## Próximo paso exacto

El endpoint temporal `/debug` fue retirado de la rama local de desarrollo y se
agregó una prueba que exige una respuesta `404`. La suite sin PostgreSQL quedó
en 31 pruebas aprobadas, 1 omitida y 1 advertencia no bloqueante.

La comparación de Dockerfiles y la auditoría pública de producción están
registradas en `AUDITORIA_PRODUCCION_LECTURA_2026-08-01.md`.

Las primeras fases de modularización extrajeron configuración, normalización,
autenticación/permisos, modelos Pydantic y las funciones PostgreSQL básicas hacia `provincia_api/`.
`main.py` reexporta los símbolos anteriores para preservar compatibilidad. La
suite quedó en 39 aprobadas, 1 omitida y 1 advertencia; el OpenAPI canónico
coincide exactamente con el commit anterior.

Las operaciones extraídas de inserción y actualización cuentan además con
rollback y cierre defensivo ante fallos de cursor, ejecución, lectura o commit.
Las fallas durante la propia limpieza no ocultan la excepción original. La
suite posterior quedó en 47 aprobadas, 1 omitida y 1 advertencia.

La rama `integracion-local-sobre-github` fue respaldada en `origin` hasta el
commit `24f5482`, sin merge ni despliegue. Después se extrajeron los helpers de
imágenes a `provincia_api/storage.py`; la suite quedó en 55 aprobadas, 1 omitida
y 1 advertencia, con OpenAPI canónico sin cambios.

El procesamiento de imágenes fue reforzado para eliminar WebP parciales cuando
Pillow falla. Las pruebas fijan además `quality=55`, `method=6` y
`optimize=True`. Una revisión fail-closed detectó que la primera limpieza podía
borrar un destino preexistente; se corrigió mediante creación exclusiva y
pruebas de colisión. La suite quedó en 63 aprobadas, 1 omitida y 1 advertencia.

1. Completar la comparación estructural de PostgreSQL con defaults,
   constraints, índices y secuencias, sin consultar filas.
2. Identificar la configuración de respaldos de base y `/data` sin mostrar
   secretos ni datos personales.
3. Documentar el procedimiento actual de despliegue en Coolify.
4. Preparar un procedimiento de publicación con respaldo, comprobaciones
   posteriores y reversión.
5. Caracterizar por separado cada bloque SQL restante antes de extraerlo; no
   mover todavía paneles ni HTML.
6. Separar helpers de payloads de webhook sólo después de caracterizar JSON,
   formularios y archivos, manteniendo el endpoint en `main.py`.

No modificar producción, no integrar historiales y no desplegar sin autorización
expresa.
