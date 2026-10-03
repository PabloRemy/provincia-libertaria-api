import os
from pathlib import Path

import psycopg2
import pytest


def database_url_for_tests():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL no configurada")

    database_name = url.rsplit("/", 1)[-1].split("?", 1)[0]
    if not database_name.endswith("_test"):
        pytest.fail("La base de pruebas debe terminar en _test")

    return url


@pytest.mark.database
def test_schema_permite_insertar_un_incidente():
    url = database_url_for_tests()
    schema = Path("sql/test_schema.sql").read_text(encoding="utf-8")

    with psycopg2.connect(url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(schema)
            cursor.execute(
                """
                INSERT INTO incidentes
                    (ciudad, barrio, categoria, descripcion)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                ("Berisso", "Centro", "Alumbrado", "Prueba automatizada"),
            )
            assert cursor.fetchone()[0] > 0
        connection.rollback()
