# Estado actual de Provincia Libertaria

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
- Los historiales de ambas ramas son independientes y no tienen ancestro común.
  No se deben mezclar mediante `pull`, merge o rebase automático.
- `integracion-local-sobre-github` es la fuente de verdad técnica para el
  desarrollo; `main` conserva la referencia productiva e histórica.

## Estado real del proyecto

Provincia Libertaria es un prototipo funcional avanzado con una línea base local
completa y reproducible. FastAPI, PostgreSQL, WordPress, CF7, paneles, mapa,
autenticación, fotos y persistencia fueron validados en el entorno aislado. El
proyecto aún no tiene una línea base comparada contra lo desplegado en
producción.

La **Etapa 4 — Validación funcional** está completada para los recorridos locales
registrados en esta línea base. Permanecen fuera de este cierre la comparación
productiva y otros recorridos sin cobertura suficiente.
La **Etapa 4.5 — Orden interno de `main.py`** está planificada, pero no comenzó.
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
- Suite completa con `TEST_DATABASE_URL`: 31 aprobadas y 1 advertencia.
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

- `main.py`: aplicación completa. Contiene configuración, modelos, acceso a
  datos, autenticación, imágenes, webhooks, rutas, paneles y HTML.
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

El árbol Git estuvo limpio antes y después de las validaciones. Los únicos
cambios previstos en esta tarea son documentales. No se modificaron `main.py`,
Docker, Compose, tests, SQL, WordPress ni configuración funcional.

## Qué NO se debe tocar

- No modificar producción ni conectarse a su base para hacer pruebas.
- No desplegar el estado local actual.
- No modificar `main.py` hasta volver a verificar la línea base de pruebas y
  comparar el estado de integración con producción.
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

1. `main.py` concentra toda la aplicación en aproximadamente 2.500 líneas; su
   modularización todavía no comenzó.
2. Local y producción todavía no fueron comparados.
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

1. Definir si se amplía el informe restringido para consultar nombres de
   variables, esquema y respaldo sin extraer valores ni datos personales.
2. Comparar el esquema productivo con el local sin modificar la base real.
3. Documentar el procedimiento actual de despliegue en Coolify.
4. Definir publicación, respaldo, comprobaciones posteriores y reversión.
5. Agregar pruebas de caracterización de rutas críticas.
6. Recién después iniciar la separación incremental de módulos de bajo riesgo.

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
