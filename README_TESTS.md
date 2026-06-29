# Entorno de pruebas

## Pruebas unitarias

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/pytest
```

No requieren PostgreSQL ni escriben en `/data`.

## Pruebas con PostgreSQL y Docker

Levantar PostgreSQL y FastAPI aislados, y copiar la configuración local:

```bash
sudo docker compose -f compose.test.yml up -d --wait
cp .env.test.example .env.test
set -a
source .env.test
set +a
.venv/bin/pytest
```

La API local queda disponible en:

```text
http://127.0.0.1:8000
http://127.0.0.1:8000/docs
```

WordPress local queda disponible en:

```text
http://127.0.0.1:8080
```

WordPress usa una base MySQL local independiente. Sus datos, plugins y archivos
se guardan en volúmenes Docker de pruebas.

## Cargar datos ficticios

Este comando elimina únicamente los datos de la base local `_test` y carga un
escenario conocido con Berisso, Ensenada y La Plata:

```bash
sudo docker compose -f compose.test.yml --profile tools run --rm seed-test
```

Se crean nueve reportes y tres registros de reclutamiento completamente
ficticios. Puede repetirse cuando se necesite recuperar el escenario inicial.

La prueba crea las tablas necesarias, inserta un registro dentro de una
transacción y hace `rollback`. Si `TEST_DATABASE_URL` no está definida, se
omite. Si el nombre de base no termina en `_test`, falla antes de conectarse.

Detener el entorno conservando temporalmente sus datos:

```bash
sudo docker compose -f compose.test.yml down
```

Detener todo y eliminar completamente PostgreSQL, WordPress y sus archivos
descartables:

```bash
sudo docker compose -f compose.test.yml down -v
```
