from unittest.mock import patch

from starlette.staticfiles import StaticFiles


original_static_files_init = StaticFiles.__init__


def init_static_files_without_directory_check(self, *args, **kwargs):
    kwargs["check_dir"] = False
    original_static_files_init(self, *args, **kwargs)


with patch.object(StaticFiles, "__init__", init_static_files_without_directory_check):
    from main import app


def test_home_returns_application_status():
    home_route = next(
        route
        for route in app.routes
        if route.path == "/" and "GET" in route.methods
    )

    assert home_route.endpoint() == {
        "status": "ok",
        "app": "Provincia Libertaria API",
    }
