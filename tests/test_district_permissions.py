from unittest.mock import patch

import pytest
from fastapi import HTTPException
from starlette.staticfiles import StaticFiles


original_static_files_init = StaticFiles.__init__


def init_static_files_without_directory_check(self, *args, **kwargs):
    kwargs["check_dir"] = False
    original_static_files_init(self, *args, **kwargs)


with patch.object(StaticFiles, "__init__", init_static_files_without_directory_check):
    from main import puede_ver_distrito, requiere_distrito


def test_alcance_todos_puede_ver_cualquier_distrito():
    admin = {"scope": "todos"}

    assert puede_ver_distrito(admin, "berisso") is True
    assert puede_ver_distrito(admin, "quilmes") is True


def test_alcance_tercera_seccion_puede_ver_sus_distritos():
    admin = {"scope": "tercera-seccion"}

    assert puede_ver_distrito(admin, "berisso") is True
    assert puede_ver_distrito(admin, "ensenada") is True
    assert puede_ver_distrito(admin, "la-plata") is True


def test_alcance_tercera_seccion_no_puede_ver_otro_distrito():
    admin = {"scope": "tercera-seccion"}

    assert puede_ver_distrito(admin, "quilmes") is False


def test_alcance_de_distrito_solo_puede_ver_ese_distrito():
    admin = {"scope": "berisso"}

    assert puede_ver_distrito(admin, "berisso") is True
    assert puede_ver_distrito(admin, "ensenada") is False


def test_requiere_distrito_permite_acceso_autorizado():
    admin = {"scope": "berisso"}

    assert requiere_distrito("berisso", admin) is None


def test_requiere_distrito_rechaza_acceso_no_autorizado():
    admin = {"scope": "berisso"}

    with pytest.raises(HTTPException) as error:
        requiere_distrito("ensenada", admin)

    assert error.value.status_code == 403
    assert error.value.detail == "No tenés permiso para ver este distrito"
