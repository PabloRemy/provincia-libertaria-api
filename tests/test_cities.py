from unittest.mock import patch

from starlette.staticfiles import StaticFiles


original_static_files_init = StaticFiles.__init__


def init_static_files_without_directory_check(self, *args, **kwargs):
    kwargs["check_dir"] = False
    original_static_files_init(self, *args, **kwargs)


with patch.object(StaticFiles, "__init__", init_static_files_without_directory_check):
    from main import ciudad_desde_slug, slug_desde_ciudad


def test_slug_desde_ciudad_con_ciudad_conocida():
    assert slug_desde_ciudad("La Plata") == "la-plata"


def test_slug_desde_ciudad_normaliza_espacios_y_mayusculas():
    assert slug_desde_ciudad("  lanús  ") == "lanus"


def test_slug_desde_ciudad_desconocida_usa_formato_url():
    assert slug_desde_ciudad("Mar del Plata") == "mar-del-plata"


def test_slug_desde_ciudad_vacia_usa_berisso():
    assert slug_desde_ciudad(None) == "berisso"


def test_ciudad_desde_slug_con_distrito_conocido():
    assert ciudad_desde_slug("la-plata") == "La Plata"


def test_ciudad_desde_slug_desconocido_lo_convierte_en_titulo():
    assert ciudad_desde_slug("mar-del-plata") == "Mar Del Plata"
