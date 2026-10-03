# Continuar desde aquí

## Punto de reanudación confirmado — cierre productivo 2026-10-03

Producción ejecuta `main` en `e9a9b0627a9de12ffa4a05fb6ceeec5dab066dce`.
Coolify terminó el Redeploy manual autorizado; el push por sí solo no activó
auto-deploy. La imagen productiva tiene ese SHA y el contenedor
`n85p5qn4eo94demg4mnbfu3m-174729087945` está running. Pablo verificó en
`https://mapa.provincialibertaria.com/login` el acceso territorial, la barra
de sesión, `Salir` y la exigencia de login tras logout. QA de lectura confirmó
`/login` 200, `/debug` 404, `/` 200, PostgreSQL ready, fotos 28/28 y
`/data/admin_sessions.sqlite3` existente.

La rama técnica `integracion-local-sobre-github` sigue siendo la línea de
desarrollo; su HEAD documental actual es
`6d07264405df4bd16f8dfb3f3466618bff5f7539`. El corte de código validado
para el release fue `c7c19af` y pasó `74 passed, 1 warning` de
Starlette, Dockerfile, login, scopes, logout y escritura en `DATA_DIR`. El
commit de reconciliación `e9a9b06` tiene padre inmediato `abc9807` y árbol
`b65a8c3ff144d46de1f0dcb0e755f6c2e76770cf`, idéntico al de `c7c19af`;
se publicó mediante fast-forward, sin mezclar las historias independientes.
El worktree temporal de `main` sigue en `/tmp/provincia-libertaria-main-20261003`.

Pablo confirmó que enlazó manualmente el candado de «Distritos» del sitio
público a `https://mapa.provincialibertaria.com/login`. El recorrido visible
queda: sitio público → Distritos → candado → `/login` → autenticación → panel
territorial protegido → logout → `/login`. Login, sesión, panel y logout ya
habían sido verificados visual y técnicamente en el QA productivo; esta
confirmación del enlace no implica una nueva auditoría de WordPress.

Antes del release se verificó un backup local exitoso de la base
`provincia_libertaria` y uno íntegro de `/data/incidentes-fotos` (28 WebP).
Ambos están en el mismo VPS: sirven para recuperación operativa, pero no son
una copia externa. `SESSION_SECRET_KEY` está presente sólo en runtime de
Coolify. El montaje `/data/incidentes-fotos` → `/data` es de tipo **bind**,
no un volumen Docker con nombre. El aviso de configuración no aplicada
desapareció tras el Redeploy; su campo histórico exacto no pudo identificarse.

No quedan bloqueantes pendientes de este release. Mejoras opcionales: segunda
copia de backups fuera del VPS y evaluación separada de Traefik 3.6.17 →
3.6.25; v3.7 requiere revisión aparte. El próximo trabajo funcional debe
definirse con Pablo. La evolución técnica aún válida figura en
`ESTADO_ACTUAL.md`; no repetir la preparación de este despliegue.

Antes de ordenar otra auditoría de infraestructura: leer
`../nexo-central/INFRAESTRUCTURA_COOLIFY.md`,
`../nexo-central/proyectos/provincia-libertaria.md`, este documento y
`ESTADO_ACTUAL.md`; consultar a Pablo si el punto pudo haber sido configurado
manualmente; auditar sólo el dato que siga realmente desconocido.

La documentación posterior conserva la cronología de validaciones anteriores;
este punto de reanudación prevalece sobre sus indicaciones ya superadas.

## Cronología anterior — superada por el cierre productivo anterior

## Bloque de login ya publicado en la rama remota — 2026-10-03

La rama `integracion-local-sobre-github` incorpora un
login web con sesiones, logout y las mismas reglas de `ADMIN_USERS` y scopes.
El bloque inicial de login pasó 71 pruebas y una advertencia. El commit
`1dd7052` fue publicado en la rama de integración, sin despliegue. El entorno
de pruebas necesita `SESSION_SECRET_KEY`
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
- Rama productiva en aquel corte: `main` en `abc9807`.
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

La reconciliación posterior quedó registrada en el punto de reanudación vigente.

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

## Próximo paso del corte histórico 2026-08-01 — ya superado donde corresponda

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
