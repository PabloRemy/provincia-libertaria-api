# Estado actual de Provincia Libertaria

## Estado productivo y preparación — corte 2026-10-03

Desarrollo: `integracion-local-sobre-github` quedó sincronizada con `origin` en
`34f19f4` y con árbol limpio tras el push. El Dockerfile canónico construyó y
arrancó localmente; `/`, `/login` y `/tablero` respondieron 200. Login, scopes,
logout, escritura en `DATA_DIR` y `admin_sessions.sqlite3` fueron validados con
datos ficticios, además de la aprobación visual de Pablo. Suite completa:
`74 passed, 1 warning` conocido de Starlette. Estos cambios no se desplegaron.

Producción: el contenedor `n85p5qn4eo94demg4mnbfu3m-132351845310` continúa
en `abc9807bba2974ecd1bab36aa80166de3c66fbdf` bajo
`https://mapa.provincialibertaria.com`. En la auditoría de lectura respondieron
correctamente `/`, `/tablero` y `/reportes/berisso`. `/login` todavía no existe
y `/territorio/berisso` conserva HTTP Basic. `/debug` sigue expuesto en el
OpenAPI histórico; la rama nueva lo eliminó y comprueba su 404, sin requerir un
cambio productivo separado.

Pablo confirmó visualmente en Coolify la Application
`provincia-libertaria-api:main-a10pfhw4ldlkafu6m7bh4p78` dentro de
`ProvinciaLibertaria / production`: fuente Public GitHub
`PabloRemy/provincia-libertaria-api`, rama `main`, Commit SHA `HEAD`, Build Pack
`Dockerfile`, Base Directory `/`, Dockerfile Location `/Dockerfile` y dominio
indicado arriba. El Dockerfile de `34f19f4` coincide con esa ubicación. Main e
integración conservan historiales independientes.

Coolify advierte `1 unapplied configuration change detected. A rebuild is
required.` La vista de cambios mostró sólo "Previously deployed configuration
-> Current configuration", sin campo identificable; no se aplicó. En
Configuration > Rollback figuran `Images to keep for rollback: 2` y la imagen
`abc9807bba2974ecd1bab36aa80166de3c66fbdf`, fechada
`2026-06-19 13:24:33 +0000 UTC`, con acción Rollback disponible. No se ejecutó
y no se presume retención adicional.

Persistent Storage muestra el volumen
`n85p5qn4eo94demg4mnbfu3m-incidentes-fotos`, Source Path
`/data/incidentes-fotos` y Destination Path `/data`. El nuevo código usa
`DATA_DIR=/data` por defecto: uploads y, después de un despliegue, el SQLite de
sesiones quedarían en ese bind mount. El PostgreSQL principal compartido está
documentado desde el snapshot 2026-09-28 en
`../nexo-central/INFRAESTRUCTURA_COOLIFY.md`; Provincia usa la base
`provincia_libertaria`. La agrupación visual del recurso PostgreSQL en
`Pardementes / production` no lo vuelve exclusivo de Par de Mentes.

Variables productivas, sólo presencia: `DATABASE_URL` y `ADMIN_USERS`
presentes; `DATA_DIR` ausente (default `/data`); `SESSION_SECRET_KEY` ausente;
`SESSION_COOKIE_SECURE` ausente (default seguro para HTTPS). No se registraron
valores. Falta agregar `SESSION_SECRET_KEY` en Environment Variables antes de
un despliegue autorizado.

Persistencia PostgreSQL y `/data`: confirmada. Backup recuperable de
`provincia_libertaria` y backup independiente de `/data/incidentes-fotos`:
pendientes de verificar o crear. También faltan identificar el cambio de
configuración no aplicado y definir publicación controlada de la rama técnica
sin mezclar historiales. Éstos son los bloqueantes reales; producción no fue
modificada. La cronología de abajo describe cortes anteriores.

## Construcción Docker local — 2026-10-03

La auditoría productiva del 2026-10-03 confirmó que producción sigue en
`abc9807`. El `Dockerfile.txt` histórico copiaba sólo `main.py`; el código de
`1dd7052` importa además `provincia_api/`, por lo que esa receta no permite
iniciar la aplicación actual. Se agregó `Dockerfile` como receta canónica
propuesta para el próximo despliegue y se corrigió `Dockerfile.test`; ambas
copian `main.py` y `provincia_api/` tras instalar `requirements.txt`.

Las dos imágenes construyeron localmente. La imagen canónica arrancó en un
contenedor aislado con PostgreSQL y usuarios ficticios: `/`, `/login` y
`/tablero` respondieron 200; `admin-test` y `berisso-test` accedieron a sus
paneles y, tras POST `/logout`, volvieron al login. Se verificaron imports,
escritura en `DATA_DIR` y creación de `admin_sessions.sqlite3`. La suite
completa pasó con 74 pruebas y una advertencia conocida de Starlette.
Producción no fue modificada; el despliegue sigue pendiente.

## Actualización local — 2026-10-03

En `integracion-local-sobre-github`, sin despliegue, se reemplazó
HTTP Basic de administración por `/login`, cookie de sesión firmada y registro
local de sesiones activas en `DATA_DIR/admin_sessions.sqlite3`. `/logout`
elimina la sesión. `ADMIN_USERS` y los permisos territoriales siguen vigentes.
Se requiere `SESSION_SECRET_KEY` de entorno (mínimo 32 caracteres); sin él, el
acceso administrativo falla cerrado. El bloque inicial de login pasó 71 pruebas
y una advertencia de Starlette. Los párrafos históricos de este
documento reflejan la línea base anterior al bloque.

Pablo validó manual y visualmente el bloque local: `/login` se muestra
correctamente; `admin-test` inicia sesión con scope `todos`; `berisso-test`
inicia sesión y llega al panel de Berisso. El flujo visual y funcional quedó
aprobado localmente. Producción no fue modificada.

La continuación local agregó un elemento de sesión reutilizado en Tercera
Sección, paneles distritales y edición de reportes. Muestra usuario, alcance y
`Salir`, que envía POST a `/logout`. La sesión queda invalidada y las rutas
administrativas vuelven a exigir login. La suite completa quedó en 74 pruebas
aprobadas y una advertencia de Starlette. Pablo aprobó visualmente también la
barra, el logout y el reingreso con otro usuario en el entorno local.

Fecha de referencia: 14 de julio de 2026. Validaciones realizadas el 13/14 de
julio de 2026.

## Estado Git y sincronización

- Clon local: `/home/desk/Documentos/Proyectos/provincia-libertaria-api`.
- Rama activa de desarrollo: `integracion-local-sobre-github`, publicada como
  `origin/integracion-local-sobre-github` en `2a8b556` al comenzar las
  validaciones.
- Rama productiva: `main`; `origin/main` está en `abc9807`.
- El OpenAPI público y la etiqueta de la imagen productiva confirman
  `origin/main` en `abc9807bba2974ecd1bab36aa80166de3c66fbdf`.
- Se verificó un acceso SSH dedicado y restringido que sólo ejecuta un informe
  de metadatos del contenedor sin mostrar secretos.
- La auditoría ampliada confirmó nombres de configuración sin valores, el bind
  mount `/data/incidentes-fotos` y dos tablas productivas con 25 columnas.
- El esquema productivo difiere de `sql/test_schema.sql` en tipos, nulabilidad y
  la columna `reclutamiento_registros.origen`.
- Los historiales de ambas ramas son independientes y no tienen ancestro común.
  No se deben mezclar mediante `pull`, merge o rebase automático.
- `integracion-local-sobre-github` es la fuente de verdad técnica para el
  desarrollo; `main` conserva la referencia productiva e histórica.

## Estado real del proyecto

Provincia Libertaria es un prototipo funcional avanzado con una línea base local
completa y reproducible. FastAPI, PostgreSQL, WordPress, CF7, paneles, mapa,
autenticación, fotos y persistencia fueron validados en el entorno aislado. El
contrato público, la imagen desplegada, el esquema PostgreSQL y la persistencia
de imágenes fueron comparados en modo lectura contra producción.

La **Etapa 4 — Validación funcional** está completada para los recorridos locales
registrados en esta línea base. Permanecen fuera de este cierre la comparación
productiva y otros recorridos sin cobertura suficiente.
La **Etapa 4.5 — Orden interno de `main.py`** avanzó con extracciones
conservadoras de configuración, normalización, autenticación/permisos y modelos
Pydantic. También se extrajeron las tres funciones básicas de acceso PostgreSQL
para conexión, inserción de incidentes y actualización de estado. Las dos
operaciones transaccionales extraídas ahora intentan rollback y cierre completo
ante fallos sin ocultar la excepción original. Los helpers de procesamiento y
resolución de imágenes también fueron separados en un módulo propio y eliminan
archivos parciales si Pillow falla durante la escritura. El destino se crea de
forma exclusiva para no sobrescribir ni borrar archivos preexistentes.
No existe todavía un procedimiento probado de publicación, respaldo y
reversión.

## Qué funciona hoy

- API FastAPI con endpoint de estado en `/`.
- Registro de reclutamiento mediante `/registro`.
- Alta de incidentes mediante JSON, formulario y multipart.
- Recepción de fotos por archivo, Base64 o URL.
- Conversión de imágenes locales a WebP.
- Persistencia en PostgreSQL.
- Estados de incidentes: `pendiente`, `publicado`, `resuelto` y `oculto`.
- Autenticación HTTP Basic para administración.
- Permisos globales, por Tercera Sección y por distrito.
- Panel general de Tercera Sección y paneles distritales.
- Edición y moderación individual o por lote.
- Vistas públicas de reportes.
- Tablero territorial con Leaflet y OpenStreetMap.
- Linux Mint 22.3 Zena, base Ubuntu Noble `amd64`, Python 3.12.3 y `.venv`.
- Docker Engine y Docker Compose instalados y validados con `hello-world`.
- Entorno Docker local aislado con `postgres-test`, `api-test`,
  `mysql-wordpress-test` y `wordpress-test` saludables.
- Datos ficticios reproducibles para Berisso, Ensenada y La Plata.
- Suite sin PostgreSQL: 30 aprobadas, 1 deseleccionada y 1 advertencia.
- Suite completa con `TEST_DATABASE_URL`: 31 aprobadas y 1 advertencia en la
  línea base Docker.
- Suite posterior al refuerzo de almacenamiento: 63 aprobadas, 1 omitida y 1
  advertencia; OpenAPI canónico sin cambios frente al commit anterior.
- FastAPI `/`, `/docs` y `/openapi.json` respondieron 200.
- Panel de Tercera Sección, paneles de Berisso, Ensenada y La Plata, tablero,
  marcadores ficticios y autenticación administrativa validados visualmente.
- WordPress y CF7 validados con y sin foto mediante el mu-plugin local.
- Carga CF7 con foto validada extremo a extremo: persistencia de `foto_url`,
  creación WebP, visualización mediante `/foto/...` y panel de Berisso.
- Persistencia comprobada tras detener sin `-v` y volver a levantar el entorno.

La incidencia anterior de imágenes desde CF7 local ya no se reproduce en el
entorno actual. Este resultado no confirma el comportamiento de producción ni
implica que allí se haya corregido nada.

## Archivos importantes

- `main.py`: punto de entrada y aplicación todavía principal; conserva modelos,
  acceso a datos, imágenes, webhooks, rutas, paneles y HTML.
- `provincia_api/config.py`: rutas de almacenamiento, estados y distritos.
- `provincia_api/normalization.py`: normalización y conversión ciudad/slug.
- `provincia_api/auth.py`: autenticación HTTP Basic y permisos territoriales.
- `provincia_api/models.py`: modelos Pydantic de reclutamiento, incidentes y
  fotografías JSON/Base64.
- `provincia_api/database.py`: conexión PostgreSQL, inserción normalizada de
  incidentes y actualización de estados.
- `provincia_api/storage.py`: validación, conversión WebP, Base64 y resolución de
  URLs públicas de fotografías.
- `tests/test_module_boundaries.py`: compatibilidad de símbolos reexportados por
  `main.py` durante la modularización incremental.
- `compose.test.yml`: servicios Docker del entorno local de pruebas.
- `Dockerfile.test`: imagen local de la API.
- `Dockerfile.txt`: definición histórica o productiva de la imagen; no asumir
  que coincide con el VPS sin verificarlo.
- `requirements.txt`: dependencias de ejecución.
- `requirements-dev.txt`: dependencias adicionales de pruebas.
- `pytest.ini`: configuración de pytest.
- `.env.test.example`: variables ficticias para el entorno descartable.
- `README_TESTS.md`: instrucciones para ejecutar el entorno y las pruebas.
- `sql/test_schema.sql`: esquema descartable local.
- `sql/test_seed.sql`: datos ficticios reproducibles.
- `tests/`: pruebas automáticas existentes.
- `wordpress/`: formulario, configuración y documentación de CF7 local.
- `00_PROVINCIA_LIBERTARIA_MASTER.md`: visión funcional del producto.
- `01_DESARROLLO_TECNICO.md`: stack y funcionalidades declaradas.
- `02_MAPA_DE_RUTA_ENTORNO_DE_PRUEBAS.md`: continuidad técnica y etapas.

Los directorios `.venv/`, `.pytest_cache/` y `__pycache__/` son artefactos
locales ignorados por Git; no son código fuente.

## Estado del árbol de trabajo

La primera modularización modifica sólo código Python, pruebas y documentación.
No modifica Docker, Compose, SQL, WordPress ni configuración productiva.

## Qué NO se debe tocar

- No modificar producción ni conectarse a su base para hacer pruebas.
- No desplegar el estado local actual.
- No desplegar la modularización hasta completar pruebas, revisión independiente,
  respaldo verificable y procedimiento de reversión.
- No mezclar automáticamente `main` e `integracion-local-sobre-github`.
- No ejecutar `git reset --hard`, `git clean`, `git checkout --` ni operaciones
  equivalentes sobre trabajo no revisado.
- No apuntar `DATABASE_URL` o `TEST_DATABASE_URL` a producción.
- No ejecutar `sql/test_schema.sql` ni `sql/test_seed.sql` contra una base real.
- No cambiar URLs, campos de WordPress/CF7 o esquema de base durante el orden
  inicial.
- No agregar funcionalidades nuevas antes de estabilizar la línea base.
- No copiar secretos ni datos personales de producción al entorno local.

## Riesgos actuales

1. `main.py` todavía concentra 2.123 líneas con SQL de endpoints, rutas de
   imágenes, webhooks, paneles y HTML; la modularización sigue siendo inicial.
2. La comparación productiva de defaults, constraints, índices y secuencias
   todavía está pendiente.
3. Las dependencias de `requirements.txt` no tienen versiones fijadas.
4. Las pruebas no cubren suficientemente paneles, moderación, archivos,
   edición, vistas públicas y recorridos completos.
5. La retirada local de `/debug` todavía no fue comparada ni aplicada en
   producción.
6. Los endpoints públicos no muestran rate limiting ni límites explícitos de
   payload.
7. Algunas rutas devuelven detalles de excepciones internas al cliente.
8. Las conexiones PostgreSQL se manejan manualmente y no siempre garantizan
   cierre o rollback frente a errores.
9. No existe un sistema de migraciones versionadas.
10. No hay procedimiento probado de respaldo, despliegue y reversión.
11. La producción no fue validada con CF7 ni comparada con el entorno local.

## Mejora técnica no bloqueante

- Pytest informa una `StarletteDeprecationWarning` por el uso de `httpx` con
  `starlette.testclient`. No afecta el resultado actual de 30/31 pruebas.

## Próximo paso recomendado

1. Completar la comparación PostgreSQL de defaults, constraints, índices y
   secuencias sin consultar filas.
2. Identificar la configuración de respaldos de base y uploads sin extraer
   secretos ni datos personales.
3. Documentar el procedimiento actual de despliegue en Coolify.
4. Definir publicación, respaldo, comprobaciones posteriores y reversión.
5. Aplicar el mismo ciclo de caracterización a cada bloque SQL restante antes
   de moverlo; no asumir que el refuerzo cubre consultas aún embebidas en rutas.
6. Caracterizar y separar helpers de payloads de webhook sin mover todavía el
   endpoint ni alterar los monkeypatches CF7.
7. Mantener `main.py` como punto de entrada y comprobar OpenAPI y suite completa
   después de cada extracción.

## Comandos básicos para pruebas

Crear el entorno Python e instalar dependencias:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
```

Ejecutar sólo pruebas sin PostgreSQL:

```bash
.venv/bin/pytest -q -m "not database"
```

Levantar el entorno local aislado:

```bash
docker compose -f compose.test.yml up -d --wait
```

Cargar las variables locales y ejecutar toda la suite:

```bash
set -a
source .env.test
set +a
.venv/bin/pytest -q
```

Restablecer los datos ficticios locales:

```bash
docker compose -f compose.test.yml --profile tools run --rm seed-test
```

Ver el estado de los servicios:

```bash
docker compose -f compose.test.yml ps
```

Detener el entorno conservando volúmenes:

```bash
docker compose -f compose.test.yml down
```

Eliminar volúmenes sólo cuando se haya confirmado que son exclusivamente los
volúmenes descartables definidos por `compose.test.yml`:

```bash
docker compose -f compose.test.yml down -v
```

## Regla de trabajo con Git

- Ejecutar `git status --short --branch` antes y después de cada tarea.
- Revisar `git diff` antes de modificar un archivo que ya tenga cambios.
- Un commit debe representar una sola intención verificable.
- No mezclar refactor, cambios funcionales y cambios de infraestructura.
- Ejecutar las pruebas relevantes antes de cada commit.
- No agregar `.env`, secretos, volúmenes, uploads, cachés ni `.venv`.
- No reescribir ni borrar trabajo local que no haya sido identificado.
- No hacer push ni desplegar sin autorización expresa.
- Etiquetar o registrar el punto exacto que corresponde a producción antes de
  preparar una actualización.

## Checklist antes de producción

- [ ] Identificar exactamente qué commit o archivos ejecuta producción.
- [ ] Comparar código local y productivo en modo de solo lectura.
- [ ] Comparar el esquema local y productivo sin modificar la base real.
- [ ] Revisar y cerrar todos los cambios locales sin commit.
- [ ] Confirmar que no se incluyen `.env`, secretos ni datos reales.
- [ ] Fijar y revisar las versiones de dependencias.
- [x] Levantar y validar el entorno Docker local.
- [x] Ejecutar la suite completa y registrar el resultado.
- [ ] Probar alta, edición, moderación y publicación de reportes en local.
- [ ] Probar autenticación y permisos de todos los alcances.
- [ ] Probar reclutamiento, GPS y fotos de extremo a extremo.
- [x] Validar imágenes CF7 extremo a extremo en local.
- [x] Retirar `/debug` de la rama local y agregar una prueba de regresión.
- [ ] Revisar exposición de errores, payloads y datos personales.
- [ ] Preparar un respaldo verificable de base y archivos.
- [ ] Definir migraciones y orden de despliegue.
- [ ] Definir comprobaciones posteriores al despliegue.
- [ ] Definir y ensayar el procedimiento de reversión.
- [ ] Obtener autorización expresa antes de tocar producción.
