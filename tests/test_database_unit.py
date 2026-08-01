from unittest.mock import patch

import pytest
from fastapi import HTTPException
from starlette.staticfiles import StaticFiles


original_static_files_init = StaticFiles.__init__


def init_static_files_without_directory_check(self, *args, **kwargs):
    kwargs["check_dir"] = False
    original_static_files_init(self, *args, **kwargs)


class ErrorPostgresEsperado(RuntimeError):
    pass


class CursorFalso:
    def __init__(
        self,
        *,
        returned_id=41,
        rowcount=0,
        error_execute=None,
        error_fetchone=None,
        error_close=None,
    ):
        self.returned_id = returned_id
        self.rowcount = rowcount
        self.error_execute = error_execute
        self.error_fetchone = error_fetchone
        self.error_close = error_close
        self.executions = []
        self.closed = False

    def execute(self, query, params):
        if self.error_execute:
            raise self.error_execute
        self.executions.append((query, params))

    def fetchone(self):
        if self.error_fetchone:
            raise self.error_fetchone
        return (self.returned_id,)

    def close(self):
        self.closed = True
        if self.error_close:
            raise self.error_close


class ConexionFalsa:
    def __init__(
        self,
        cursor,
        *,
        error_cursor=None,
        error_commit=None,
        error_rollback=None,
        error_close=None,
    ):
        self._cursor = cursor
        self.error_cursor = error_cursor
        self.error_commit = error_commit
        self.error_rollback = error_rollback
        self.error_close = error_close
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self):
        if self.error_cursor:
            raise self.error_cursor
        return self._cursor

    def commit(self):
        if self.error_commit:
            raise self.error_commit
        self.committed = True

    def rollback(self):
        self.rolled_back = True
        if self.error_rollback:
            raise self.error_rollback

    def close(self):
        self.closed = True
        if self.error_close:
            raise self.error_close


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


@pytest.mark.parametrize("etapa", ["cursor", "execute", "fetchone", "commit"])
def test_insertar_incidente_hace_rollback_y_cierra_ante_error(monkeypatch, etapa):
    import provincia_api.database as database

    error = ErrorPostgresEsperado(etapa)
    cursor = CursorFalso(
        error_execute=error if etapa == "execute" else None,
        error_fetchone=error if etapa == "fetchone" else None,
    )
    connection = ConexionFalsa(
        cursor,
        error_cursor=error if etapa == "cursor" else None,
        error_commit=error if etapa == "commit" else None,
    )
    monkeypatch.setattr(database, "db_conn", lambda: connection)

    with pytest.raises(ErrorPostgresEsperado) as captured:
        database.insertar_incidente(
            ciudad="Berisso",
            barrio="Centro",
            categoria="Alumbrado",
            descripcion="Prueba",
        )

    assert captured.value is error
    assert connection.rolled_back is True
    assert connection.closed is True
    assert cursor.closed is (etapa != "cursor")


@pytest.mark.parametrize("etapa", ["cursor", "execute", "commit"])
def test_actualizar_estado_hace_rollback_y_cierra_ante_error(monkeypatch, etapa):
    import provincia_api.database as database

    error = ErrorPostgresEsperado(etapa)
    cursor = CursorFalso(error_execute=error if etapa == "execute" else None)
    connection = ConexionFalsa(
        cursor,
        error_cursor=error if etapa == "cursor" else None,
        error_commit=error if etapa == "commit" else None,
    )
    monkeypatch.setattr(database, "db_conn", lambda: connection)

    with pytest.raises(ErrorPostgresEsperado) as captured:
        database.actualizar_estado_incidentes([1, 2], "publicado")

    assert captured.value is error
    assert connection.rolled_back is True
    assert connection.closed is True
    assert cursor.closed is (etapa != "cursor")


def test_limpieza_no_oculta_error_original_ni_interrumpe_otros_cierres(monkeypatch):
    import provincia_api.database as database

    error_operacion = ErrorPostgresEsperado("execute")
    error_limpieza = RuntimeError("limpieza")
    cursor = CursorFalso(
        error_execute=error_operacion,
        error_close=error_limpieza,
    )
    connection = ConexionFalsa(
        cursor,
        error_rollback=error_limpieza,
        error_close=error_limpieza,
    )
    monkeypatch.setattr(database, "db_conn", lambda: connection)

    with pytest.raises(ErrorPostgresEsperado) as captured:
        database.insertar_incidente(
            ciudad="Berisso",
            barrio="Centro",
            categoria="Alumbrado",
            descripcion="Prueba",
        )

    assert captured.value is error_operacion
    assert connection.rolled_back is True
    assert cursor.closed is True
    assert connection.closed is True
