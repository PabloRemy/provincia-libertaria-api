# Estado actual de Provincia Libertaria

## Estado productivo vigente — cierre 2026-10-03

`main` ejecuta `e9a9b0627a9de12ffa4a05fb6ceeec5dab066dce` en
`https://mapa.provincialibertaria.com`. Coolify importó el commit, construyó
la imagen `n85p5qn4eo94demg4mnbfu3m:e9a9b0627a9de12ffa4a05fb6ceeec5dab066dce`
y completó el rolling update. Contenedor
`n85p5qn4eo94demg4mnbfu3m-174729087945`: running, restart
`unless-stopped`. El push fue fast-forward (`abc9807..e9a9b06`), sin force;
no disparó auto-deploy, por lo que Pablo autorizó y ejecutó Redeploy manual.

El release conserva `abc9807bba2974ecd1bab36aa80166de3c66fbdf` como
padre productivo inmediato. El HEAD actual de la rama técnica
`integracion-local-sobre-github` es
`6d07264405df4bd16f8dfb3f3466618bff5f7539`; el corte de código validado
para el release fue `c7c19af`. El árbol de `e9a9b06` y el de ese corte son
idénticos:
`b65a8c3ff144d46de1f0dcb0e755f6c2e76770cf`; `git diff --exit-code
c7c19af main` terminó en 0. No se mezclaron los historiales independientes.
La rama técnica continúa siendo la línea de desarrollo; `main`, la productiva.
El código fue validado localmente con Dockerfile canónico, login/sesiones,
scopes, logout, `DATA_DIR`, SQLite y suite `74 passed, 1 warning` conocido de
Starlette.

Pablo validó visualmente `/login`, acceso con usuario productivo a su panel,
barra de sesión, `Salir` y nuevo requisito de login tras logout. QA productivo
en lectura confirmó `/login` 200, `/debug` 404, `/` 200, PostgreSQL ready,
variables `DATABASE_URL`, `ADMIN_USERS` y `SESSION_SECRET_KEY` presentes,
`DATA_DIR=/data` y `/data/admin_sessions.sqlite3` existente (12K). La clave de
sesión se configuró en Coolify sólo para runtime, no para buildtime; no se
registra ningún valor. El fallo inicial de acceso por un error de tipeo del
usuario no fue una incidencia del sistema.

Pablo confirmó posteriormente que configuró manualmente el candado de
«Distritos» del sitio público hacia
`https://mapa.provincialibertaria.com/login`. El flujo público → Distritos →
candado → `/login` → autenticación → panel territorial protegido → logout →
`/login` queda enlazado. Login, sesión, panel y logout ya contaban con QA
productivo visual y técnico; no se realizó una nueva auditoría de WordPress.

El montaje real es **bind** de `/data/incidentes-fotos` en el host a `/data`
en el contenedor, no un volumen Docker con nombre. Fotos WebP: 28 en host y
28 en contenedor; directorio 2.1M. El PostgreSQL principal compartido
`z406pi9eggcskqpll10b1wmd` aloja `provincia_libertaria` (ver
`../nexo-central/INFRAESTRUCTURA_COOLIFY.md`).

Antes del despliegue se creó en Coolify un backup local de esa base: schedule
diario `0 3 * * *` UTC, sólo `provincia_libertaria`, retención de 7 copias,
timeout 3600, S3 desactivado. `Backup Now` terminó Success en 2 s, 8.71 KB,
con archivo local
`/data/coolify/backups/databases/root-team-0/postgresql-database-z406pi9eggcskqpll10b1wmd/z406pi9eggcskqpll10b1wmd/pg-dump-provincia_libertaria-1791046778.dmp`.
Se creó además el backup de fotos
`/data/backups/provincia-libertaria/incidentes-fotos-20261003-170702.tar.gz`:
2.0M, tar íntegro, 28/28 WebP, SHA256
`9453fc9aff878d176745509e31003250b35769e40e167586200a23c21003020e`.
El QA posterior confirmó presencia y hash. Ambos respaldos están en el mismo
VPS: permiten recuperación operativa, no disaster recovery externo.

El aviso anterior de Coolify sobre un cambio de configuración no aplicado
desapareció tras el Redeploy. La base interna de Coolify no conservaba el
deployment histórico, así que el campo anterior exacto no pudo establecerse;
el asunto está **cerrado**. Traefik continúa en 3.6.17: evaluar 3.6.25 en
otro bloque; v3.7 exige revisión aparte. No quedan bloqueantes de este release.
La copia externa de backups es una mejora opcional. El siguiente trabajo
funcional se definirá después de este cierre.

## Cronología anterior — no describe producción vigente

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
En ese bloque local producción no fue modificada; el despliegue posterior está
registrado en el estado vigente anterior.

## Actualización local anterior — 2026-10-03

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
- Rama productiva en el corte anterior: `main` en `abc9807`.
- En aquel corte, el OpenAPI público y la etiqueta de imagen confirmaban
  `abc9807bba2974ecd1bab36aa80166de3c66fbdf`.
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
El release del 2026-10-03 documentó publicación, respaldos previos y rollback
de aplicación disponible; no se ejecutó un rollback ni un restore de prueba.

## Funcionalidad registrada (incluye pruebas locales históricas)

- API FastAPI con endpoint de estado en `/`.
- Registro de reclutamiento mediante `/registro`.
- Alta de incidentes mediante JSON, formulario y multipart.
- Recepción de fotos por archivo, Base64 o URL.
- Conversión de imágenes locales a WebP.
- Persistencia en PostgreSQL.
- Estados de incidentes: `pendiente`, `publicado`, `resuelto` y `oculto`.
- Login web con sesiones, logout y scopes derivados de `ADMIN_USERS`.
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
- `provincia_api/auth.py`: autenticación administrativa por sesión y permisos
  territoriales.
- `provincia_api/models.py`: modelos Pydantic de reclutamiento, incidentes y
  fotografías JSON/Base64.
- `provincia_api/database.py`: conexión PostgreSQL, inserción normalizada de
  incidentes y actualización de estados.
- `provincia_api/storage.py`: validación, conversión WebP, Base64 y resolución de
  URLs públicas de fotografías.
- `tests/test_module_boundaries.py`: compatibilidad de símbolos reexportados por
  `main.py` durante la modularización incremental.
- `compose.test.yml`: servicios Docker del entorno local de pruebas.
- `Dockerfile`: receta canónica utilizada para la imagen productiva actual.
- `Dockerfile.test`: imagen local de la API.
- `Dockerfile.txt`: receta histórica, anterior a la arquitectura modular.
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

## Estado del árbol de trabajo en la primera modularización — histórico

La primera modularización modifica sólo código Python, pruebas y documentación.
No modifica Docker, Compose, SQL, WordPress ni configuración productiva.

## Qué NO se debe tocar

- No modificar producción ni conectarse a su base para hacer pruebas.
- Los futuros despliegues requieren autorización, validación y respaldo propios.
- No mezclar automáticamente `main` e `integracion-local-sobre-github`.
- No ejecutar `git reset --hard`, `git clean`, `git checkout --` ni operaciones
  equivalentes sobre trabajo no revisado.
- No apuntar `DATABASE_URL` o `TEST_DATABASE_URL` a producción.
- No ejecutar `sql/test_schema.sql` ni `sql/test_seed.sql` contra una base real.
- No cambiar URLs, campos de WordPress/CF7 o esquema de base durante el orden
  inicial.
- No agregar funcionalidades nuevas antes de estabilizar la línea base.
- No copiar secretos ni datos personales de producción al entorno local.

## Riesgos técnicos y pendientes de evolución

1. `main.py` todavía concentra 2.123 líneas con SQL de endpoints, rutas de
   imágenes, webhooks, paneles y HTML; la modularización sigue siendo inicial.
2. La comparación productiva de defaults, constraints, índices y secuencias
   todavía está pendiente.
3. Las dependencias de `requirements.txt` no tienen versiones fijadas.
4. Las pruebas no cubren suficientemente paneles, moderación, archivos,
   edición, vistas públicas y recorridos completos.
5. Los endpoints públicos no muestran rate limiting ni límites explícitos de
   payload.
6. Algunas rutas devuelven detalles de excepciones internas al cliente.
7. Las conexiones PostgreSQL se manejan manualmente y no siempre garantizan
   cierre o rollback frente a errores.
8. No existe un sistema de migraciones versionadas.
9. El backup y despliegue de `e9a9b06` se comprobaron; resta probar un restore
    y, si se decide, una copia externa de los respaldos.
10. La producción no fue validada con CF7 de extremo a extremo.

## Mejora técnica no bloqueante

- Pytest informa una `StarletteDeprecationWarning` por el uso de `httpx` con
  `starlette.testclient`. No afecta las 74 pruebas aprobadas del corte vigente.

## Próximo paso recomendado

1. Completar la comparación PostgreSQL de defaults, constraints, índices y
   secuencias sin consultar filas.
2. Aplicar el mismo ciclo de caracterización a cada bloque SQL restante antes
   de moverlo; no asumir que el refuerzo cubre consultas aún embebidas en rutas.
3. Caracterizar y separar helpers de payloads de webhook sin mover todavía el
   endpoint ni alterar los monkeypatches CF7.
4. Mantener `main.py` como punto de entrada y comprobar OpenAPI y suite completa
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

## Checklist histórico antes del release — revisar por separado para cambios futuros

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
