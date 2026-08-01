from unittest.mock import patch

import pytest
from fastapi import HTTPException
from starlette.staticfiles import StaticFiles


original_static_files_init = StaticFiles.__init__


def init_static_files_without_directory_check(self, *args, **kwargs):
    kwargs["check_dir"] = False
    original_static_files_init(self, *args, **kwargs)


class CursorFalso:
    def __init__(self, *, returned_id=41, rowcount=0):
        self.returned_id = returned_id
        self.rowcount = rowcount
        self.executions = []
        self.closed = False

    def execute(self, query, params):
        self.executions.append((query, params))

    def fetchone(self):
        return (self.returned_id,)

    def close(self):
        self.closed = True


class ConexionFalsa:
    def __init__(self, cursor):
        self._cursor = cursor
        self.committed = False
        self.closed = False

    def cursor(self):
        return self._cursor

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


def test_main_reexporta_acceso_a_datos_extraido():
    from provincia_api.database import (
        actualizar_estado_incidentes,
        db_conn,
        insertar_incidente,
    )

    with patch.object(StaticFiles, "__init__", init_static_files_without_directory_check):
        import main

    assert main.db_conn is db_conn
    assert main.insertar_incidente is insertar_incidente
    assert main.actualizar_estado_incidentes is actualizar_estado_incidentes


def test_db_conn_rechaza_configuracion_faltante(monkeypatch):
    from provincia_api.database import db_conn

    monkeypatch.delenv("DATABASE_URL", raising=False)

    with pytest.raises(HTTPException) as error:
        db_conn()

    assert error.value.status_code == 500
    assert error.value.detail == "DATABASE_URL no configurada"


def test_insertar_incidente_normaliza_confirma_y_cierra(monkeypatch):
    import provincia_api.database as database

    cursor = CursorFalso(returned_id=73)
    connection = ConexionFalsa(cursor)
    monkeypatch.setattr(database, "db_conn", lambda: connection)

    result = database.insertar_incidente(
        ciudad="  la   plata ",
        barrio=" centro ",
        categoria=" alumbrado ",
        categoria_detalle="  luminaria rota ",
        descripcion="Sin luz",
        direccion="  Calle  7 ",
        foto_url="/uploads/incidentes/prueba.webp",
        estado="pendiente",
        origen="vecino",
        fuente="formulario",
        latitud=-34.92,
        longitud=-57.95,
    )

    assert result == 73
    assert cursor.executions[0][1] == (
        "La Plata",
        "Centro",
        "Alumbrado",
        "luminaria rota",
        "Sin luz",
        "Calle 7",
        "/uploads/incidentes/prueba.webp",
        "pendiente",
        "vecino",
        "formulario",
        -34.92,
        -57.95,
    )
    assert connection.committed is True
    assert cursor.closed is True
    assert connection.closed is True


def test_actualizar_estado_rechaza_estado_invalido():
    from provincia_api.database import actualizar_estado_incidentes

    with pytest.raises(HTTPException) as error:
        actualizar_estado_incidentes([1], "desconocido")

    assert error.value.status_code == 400
    assert error.value.detail == "Estado inválido"


def test_actualizar_estado_sin_ids_no_abre_conexion(monkeypatch):
    import provincia_api.database as database

    def conexion_inesperada():
        raise AssertionError("No debe abrir conexión")

    monkeypatch.setattr(database, "db_conn", conexion_inesperada)

    assert database.actualizar_estado_incidentes([], "pendiente") == 0


def test_actualizar_estado_confirma_y_cierra(monkeypatch):
    import provincia_api.database as database

    cursor = CursorFalso(rowcount=2)
    connection = ConexionFalsa(cursor)
    monkeypatch.setattr(database, "db_conn", lambda: connection)

    result = database.actualizar_estado_incidentes([5, 8], "publicado")

    assert result == 2
    assert cursor.executions[0][1] == ("publicado", [5, 8])
    assert connection.committed is True
    assert cursor.closed is True
    assert connection.closed is True
