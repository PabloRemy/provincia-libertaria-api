# Entorno local de pruebas

Línea base validada el 13/14 de julio de 2026 en Linux Mint 22.3 Zena, base
Ubuntu Noble y arquitectura `amd64`, con Python 3.12.3, Docker Engine y Docker
Compose. Docker fue comprobado previamente con `hello-world`.

El entorno usa exclusivamente credenciales ficticias, la base local
`provincia_libertaria_test` y puertos publicados en loopback. No existe conexión
con producción.

## Preparar Python y ejecutar pruebas sin PostgreSQL

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/pytest -q -m "not database"
```

Resultado validado:

```text
30 passed, 1 deselected, 1 warning
```

La advertencia es una `StarletteDeprecationWarning` relacionada con el uso de
`httpx` desde `starlette.testclient`. Es una mejora técnica no bloqueante.

## Levantar Docker y ejecutar la suite completa

Crear la configuración local ignorada por Git si todavía no existe:

```bash
cp .env.test.example .env.test
```

Levantar FastAPI, PostgreSQL, WordPress y MySQL locales:

```bash
sudo docker compose -f compose.test.yml up -d --wait
sudo docker compose -f compose.test.yml ps
```

Cargar las variables locales y ejecutar la suite completa:

```bash
set -a
source .env.test
set +a
.venv/bin/pytest -q
```

Resultado validado:

```text
31 passed, 1 warning
```

La misma advertencia de Starlette/httpx permanece como mejora no bloqueante.

Después de la primera modularización de `main.py`, la suite local sin conexión
a PostgreSQL productivo quedó en `32 passed, 1 skipped, 1 warning`. Además, el
OpenAPI canónico conservó el mismo SHA-256 antes y después del cambio:
`a9145c77182cd8d6a977c96203d4a03cd5a3b89bca65e817b34a8a70b9b59e76`.

Después de extraer también los modelos Pydantic, la suite quedó en
`33 passed, 1 skipped, 1 warning`; el mismo hash OpenAPI volvió a permanecer
sin cambios.

Después de extraer las funciones PostgreSQL básicas y agregar pruebas unitarias
con conexiones falsas, la suite quedó en `39 passed, 1 skipped, 1 warning`; el
hash OpenAPI permaneció nuevamente sin cambios. Estas pruebas cubren el camino
exitoso de commit y cierre, pero no implican que el rollback ante excepciones ya
esté resuelto.

Servicios y accesos validados:

```text
postgres-test          healthy   127.0.0.1:55432
api-test               healthy   127.0.0.1:8000
mysql-wordpress-test   healthy
wordpress-test         healthy   127.0.0.1:8080
```

Comprobaciones HTTP reproducibles:

```bash
curl -sS http://127.0.0.1:8000/
curl -sS -I http://127.0.0.1:8000/docs
curl -sS -I http://127.0.0.1:8000/openapi.json
curl -sS -I http://127.0.0.1:8080/
```

`/`, `/docs`, `/openapi.json` y WordPress respondieron correctamente; los tres
endpoints de FastAPI devolvieron estado 200. WordPress fue instalado localmente.

La base `provincia_libertaria_test` contiene las tablas `incidentes` y
`reclutamiento_registros`.

## Cargar datos ficticios

```bash
sudo docker compose -f compose.test.yml --profile tools run --rm seed-test
```

Se crean nueve incidentes y tres registros de reclutamiento completamente
ficticios. Puede repetirse cuando se necesite recuperar el escenario inicial.

La prueba de integración crea las tablas necesarias, inserta un registro dentro
de una transacción y hace `rollback`. Si `TEST_DATABASE_URL` no está definida,
se omite. Si el nombre de base no termina en `_test`, falla antes de conectarse.

## Detener conservando la persistencia

```bash
sudo docker compose -f compose.test.yml down
```

La persistencia fue validada después de ejecutar `down` sin `-v` y volver a
levantar el entorno: WordPress conservó usuario, página y formulario; PostgreSQL
conservó el incidente de prueba con foto y el archivo WebP continuó disponible.
No usar `down -v` si se desea conservar este escenario.
