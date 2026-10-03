import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from starlette.staticfiles import StaticFiles


original_static_files_init = StaticFiles.__init__


def init_static_files_without_directory_check(self, *args, **kwargs):
    kwargs["check_dir"] = False
    original_static_files_init(self, *args, **kwargs)


with patch.object(StaticFiles, "__init__", init_static_files_without_directory_check):
    import main
    from main import app, parse_admin_users


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv(
        "ADMIN_USERS",
        "pablo:clave-segura:todos,armador:clave:tercera-seccion,berisso:clave:berisso",
    )
    monkeypatch.setenv("SESSION_SECRET_KEY", "test-only-session-key-12345678901234567890")
    monkeypatch.setenv("SESSION_COOKIE_SECURE", "false")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    return TestClient(app, follow_redirects=False)


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


def test_login_form_and_invalid_credentials(client):
    form = client.get("/login")
    assert form.status_code == 200
    assert 'name="username"' in form.text
    assert 'name="password"' in form.text
    invalid = client.post("/login", data={"username": "pablo", "password": "mal"})
    assert invalid.status_code == 401
    assert "pl_admin_session" not in invalid.cookies
    assert client.get("/tercera-seccion").headers["location"] == "/login"


@pytest.mark.parametrize(
    ("username", "password", "destination"),
    [
        ("pablo", "clave-segura", "/tercera-seccion"),
        ("armador", "clave", "/tercera-seccion"),
        ("berisso", "clave", "/territorio/berisso"),
    ],
)
def test_login_redirige_segun_scope(client, username, password, destination):
    response = client.post("/login", data={"username": username, "password": password})
    assert response.status_code == 303
    assert response.headers["location"] == destination
    assert response.cookies.get("pl_admin_session")
    assert "httponly" in response.headers["set-cookie"].lower()
    assert "samesite=strict" in response.headers["set-cookie"].lower()


def test_protected_routes_redirect_without_session(client):
    for method, path, kwargs in [
        ("get", "/tercera-seccion", {}),
        ("get", "/territorio/berisso", {}),
        ("get", "/incidentes/editar/1", {}),
        ("post", "/incidentes/editar/1", {"data": {}}),
        ("post", "/incidentes/estado-lote", {"data": {}}),
    ]:
        response = getattr(client, method)(path, **kwargs)
        assert response.status_code == 303
        assert response.headers["location"] == "/login"
        assert "WWW-Authenticate" not in response.headers


def test_session_permissions_and_logout(client):
    response = client.post("/login", data={"username": "berisso", "password": "clave"})
    cookie = response.cookies["pl_admin_session"]
    assert client.get("/territorio/ensenada").status_code == 403
    assert client.get("/tercera-seccion").status_code == 403
    logout = client.post("/logout")
    assert logout.status_code == 303
    assert logout.headers["location"] == "/login"
    assert client.get("/territorio/berisso").headers["location"] == "/login"
    assert cookie != client.cookies.get("pl_admin_session")
    client.cookies.set("pl_admin_session", cookie)
    assert client.get("/territorio/berisso").headers["location"] == "/login"


def test_admin_session_bar_escapes_username_and_uses_scope_label():
    bar = main.admin_session_bar({"username": "<admin>", "scope": "berisso"})
    assert "&lt;admin&gt;" in bar
    assert "<admin>" not in bar
    assert "Berisso" in bar
    assert 'method="post" action="/logout"' in bar
    assert ">Salir</button>" in bar


def test_edit_form_shows_session_bar(client, monkeypatch):
    row = (1, "Berisso", "Centro", "Alumbrado", "", "Descripción", "",
           None, "pendiente", None, None, None)

    class Cursor:
        def execute(self, query, params):
            pass

        def fetchone(self):
            return row

        def close(self):
            pass

    class Connection:
        def cursor(self):
            return Cursor()

        def close(self):
            pass

    monkeypatch.setattr(main, "db_conn", Connection)
    client.post("/login", data={"username": "berisso", "password": "clave"})
    response = client.get("/incidentes/editar/1")
    assert response.status_code == 200
    assert "Editar reporte #1" in response.text
    assert "berisso" in response.text
    assert "Berisso" in response.text
    assert 'method="post" action="/logout"' in response.text


@pytest.mark.database
def test_management_panels_show_session_bar_and_keep_permissions(client, monkeypatch):
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL no configurada")
    database_name = url.rsplit("/", 1)[-1].split("?", 1)[0]
    if not database_name.endswith("_test"):
        pytest.fail("La base de pruebas debe terminar en _test")
    monkeypatch.setenv("DATABASE_URL", url)

    client.post("/login", data={"username": "pablo", "password": "clave-segura"})
    general = client.get("/tercera-seccion")
    assert general.status_code == 200
    assert 'aria-label="Sesión administrativa"' in general.text
    assert "pablo" in general.text
    assert "Todos los distritos" in general.text
    assert 'method="post" action="/logout"' in general.text

    client.post("/login", data={"username": "berisso", "password": "clave"})
    district = client.get("/territorio/berisso")
    assert district.status_code == 200
    assert 'aria-label="Sesión administrativa"' in district.text
    assert "berisso" in district.text
    assert "Berisso" in district.text
    assert 'method="post" action="/logout"' in district.text
    assert client.get("/territorio/ensenada").status_code == 403


def test_session_invalidates_when_password_changes(client, monkeypatch):
    client.post("/login", data={"username": "berisso", "password": "clave"})
    monkeypatch.setenv("ADMIN_USERS", "berisso:nueva-clave:berisso")
    assert client.get("/territorio/berisso").headers["location"] == "/login"


def test_missing_session_secret_fails_closed(client, monkeypatch):
    monkeypatch.delenv("SESSION_SECRET_KEY", raising=False)
    assert client.post("/login", data={"username": "pablo", "password": "clave-segura"}).status_code == 503
    assert client.get("/tercera-seccion").status_code == 503
    assert client.get("/").status_code == 200


def test_public_and_openapi_available(client):
    assert client.get("/").json()["status"] == "ok"
    schema = client.get("/openapi.json")
    assert schema.status_code == 200
    assert "/login" not in schema.json()["paths"]
    assert "/logout" not in schema.json()["paths"]
    assert "/incidente" in schema.json()["paths"]


def test_batch_return_does_not_accept_external_url(client):
    client.post("/login", data={"username": "berisso", "password": "clave"})
    response = client.post(
        "/incidentes/estado-lote",
        data={"estado": "pendiente", "volver": "https://evil.example/territorio/berisso"},
    )
    assert response.status_code == 400
