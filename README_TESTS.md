# Entorno de pruebas

## Pruebas unitarias

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/pytest
```

No requieren PostgreSQL ni escriben en `/data`.

## Pruebas con PostgreSQL y Docker

Levantar la base aislada y copiar la configuración local:

```bash
sudo docker compose -f compose.test.yml up -d --wait
cp .env.test.example .env.test
set -a
source .env.test
set +a
.venv/bin/pytest
```

La prueba crea las tablas necesarias, inserta un registro dentro de una
transacción y hace `rollback`. Si `TEST_DATABASE_URL` no está definida, se
omite. Si el nombre de base no termina en `_test`, falla antes de conectarse.

Detener PostgreSQL conservando temporalmente sus datos:

```bash
sudo docker compose -f compose.test.yml down
```

Detenerlo y eliminar completamente la base descartable:

```bash
sudo docker compose -f compose.test.yml down -v
```
