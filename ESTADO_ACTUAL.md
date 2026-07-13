# Estado actual de Provincia Libertaria

Fecha de referencia: 13 de julio de 2026.

## Estado Git y sincronización

- Clon local: `/home/desk/Documentos/Proyectos/provincia-libertaria-api`.
- Rama activa de desarrollo: `integracion-local-sobre-github`, publicada como
  `origin/integracion-local-sobre-github` en `0eafb96` al comenzar esta
  actualización documental.
- Rama productiva: `main`; `origin/main` está en `abc9807`.
- Producción continúa desplegada desde GitHub. Falta verificar qué commit exacto
  se encuentra ejecutando el VPS.
- Los historiales de ambas ramas son independientes y no tienen ancestro común.
  No se deben mezclar mediante `pull`, merge o rebase automático.
- `integracion-local-sobre-github` es la fuente de verdad técnica para el
  desarrollo; `main` conserva la referencia productiva e histórica.

## Estado real del proyecto

Provincia Libertaria es un prototipo funcional avanzado, todavía en etapa de
validación local. La API, la base de datos de pruebas, los paneles territoriales
y la integración local con WordPress están implementados, pero el proyecto aún
no tiene una línea base comprobada contra lo desplegado en producción.

La etapa real es la **Etapa 4 — Validación funcional**, parcialmente completada.
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
- Entorno Docker local aislado para API, PostgreSQL, WordPress y MySQL.
- Datos ficticios reproducibles para Berisso, Ensenada y La Plata.
- Webhook directo y envío desde CF7 local sin foto validados manualmente.
- Suite automática de pruebas unitarias y una prueba de integración PostgreSQL.

La carga de imágenes desde CF7 local no está resuelta: el incidente se guarda,
pero en el caso reproducido `foto_url` quedó vacío. La carga directa por API sí
fue validada.

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

El árbol estaba limpio al comenzar esta tarea. Los únicos cambios sin commit al
cerrarla deben ser los documentos creados o actualizados por esta sincronización:
`README.md`, `CONTINUAR_DESDE_AQUI.md` y `ESTADO_ACTUAL.md`. No se modificaron
`main.py`, Docker, tests ni configuración.

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

1. `main.py` concentra toda la aplicación en aproximadamente 2.500 líneas.
2. Local y producción todavía no fueron comparados.
3. Las dependencias de `requirements.txt` no tienen versiones fijadas.
4. Las pruebas no cubren suficientemente paneles, moderación, archivos,
   edición, vistas públicas y recorridos completos.
5. `/debug` es público y puede registrar payloads sensibles en los logs.
6. Los endpoints públicos no muestran rate limiting ni límites explícitos de
   payload.
7. Algunas rutas devuelven detalles de excepciones internas al cliente.
8. Las conexiones PostgreSQL se manejan manualmente y no siempre garantizan
   cierre o rollback frente a errores.
9. No existe un sistema de migraciones versionadas.
10. No hay procedimiento probado de respaldo, despliegue y reversión.
11. La documentación declara cantidades de pruebas anteriores al estado actual.
12. La integración de imágenes desde CF7 local continúa incompleta.

## Próximo paso recomendado

1. Levantar exclusivamente el entorno local descartable.
2. Ejecutar la suite sin PostgreSQL y luego la suite completa.
3. Registrar resultados, incluyendo la cantidad real de pruebas y cualquier
   falla reproducible.
4. Validar el contrato CF7, revisar `/debug` y confirmar la definición de
   Dockerfile que corresponde a cada entorno.
5. Inventariar producción en modo de solo lectura: versión de código, esquema,
   configuración requerida y persistencia de archivos, sin extraer secretos.
6. Comparar ese estado con `integracion-local-sobre-github` sin integrar los
   historiales automáticamente.
7. Definir respaldo, comprobaciones posteriores y reversión.
8. Agregar pruebas de caracterización de rutas críticas.
9. Recién después iniciar la separación incremental de módulos de bajo riesgo.

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
.venv/bin/pytest
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
- [ ] Construir la imagen Docker desde cero.
- [ ] Ejecutar la suite completa y registrar el resultado.
- [ ] Probar alta, edición, moderación y publicación de reportes en local.
- [ ] Probar autenticación y permisos de todos los alcances.
- [ ] Probar reclutamiento, GPS y fotos de extremo a extremo.
- [ ] Resolver o aceptar explícitamente la incidencia de imágenes CF7 local.
- [ ] Proteger o retirar `/debug`.
- [ ] Revisar exposición de errores, payloads y datos personales.
- [ ] Preparar un respaldo verificable de base y archivos.
- [ ] Definir migraciones y orden de despliegue.
- [ ] Definir comprobaciones posteriores al despliegue.
- [ ] Definir y ensayar el procedimiento de reversión.
- [ ] Obtener autorización expresa antes de tocar producción.
