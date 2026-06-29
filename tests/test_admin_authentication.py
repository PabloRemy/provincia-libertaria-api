from unittest.mock import patch

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPBasicCredentials
from starlette.staticfiles import StaticFiles


original_static_files_init = StaticFiles.__init__


def init_static_files_without_directory_check(self, *args, **kwargs):
    kwargs["check_dir"] = False
    original_static_files_init(self, *args, **kwargs)


with patch.object(StaticFiles, "__init__", init_static_files_without_directory_check):
    from main import get_current_admin, parse_admin_users


def test_parse_admin_users_interpreta_usuarios_configurados(monkeypatch):
    monkeypatch.setenv(
        "ADMIN_USERS",
        "pablo:clave-segura:todos, berisso:otra-clave:berisso",
    )

    assert parse_admin_users() == {
        "pablo": {"password": "clave-segura", "scope": "todos"},
        "berisso": {"password": "otra-clave", "scope": "berisso"},
    }


def test_parse_admin_users_ignora_entradas_incompletas(monkeypatch):
    monkeypatch.setenv("ADMIN_USERS", "incompleto, valido:clave:ensenada")

    assert parse_admin_users() == {
        "valido": {"password": "clave", "scope": "ensenada"},
    }


def test_get_current_admin_devuelve_usuario_y_alcance(monkeypatch):
    monkeypatch.setenv("ADMIN_USERS", "pablo:clave-segura:todos")
    credentials = HTTPBasicCredentials(
        username="pablo",
        password="clave-segura",
    )

    assert get_current_admin(credentials) == {
        "username": "pablo",
        "scope": "todos",
    }


def test_get_current_admin_rechaza_contrasena_incorrecta(monkeypatch):
    monkeypatch.setenv("ADMIN_USERS", "pablo:clave-segura:todos")
    credentials = HTTPBasicCredentials(
        username="pablo",
        password="incorrecta",
    )

    with pytest.raises(HTTPException) as error:
        get_current_admin(credentials)

    assert error.value.status_code == 401
    assert error.value.headers == {"WWW-Authenticate": "Basic"}


def test_get_current_admin_informa_configuracion_faltante(monkeypatch):
    monkeypatch.delenv("ADMIN_USERS", raising=False)
    credentials = HTTPBasicCredentials(username="pablo", password="cualquiera")

    with pytest.raises(HTTPException) as error:
        get_current_admin(credentials)

    assert error.value.status_code == 500
    assert error.value.detail == "ADMIN_USERS no configurado"
