from unittest.mock import patch

from starlette.staticfiles import StaticFiles


original_static_files_init = StaticFiles.__init__


def init_static_files_without_directory_check(self, *args, **kwargs):
    kwargs["check_dir"] = False
    original_static_files_init(self, *args, **kwargs)


with patch.object(StaticFiles, "__init__", init_static_files_without_directory_check):
    from main import normalizar_direccion, normalizar_numero, normalizar_texto


def test_normalizar_texto_limpia_espacios_y_aplica_mayusculas():
    assert normalizar_texto("  la   plata ") == "La Plata"


def test_normalizar_texto_conserva_valor_nulo():
    assert normalizar_texto(None) is None


def test_normalizar_direccion_limpia_espacios_sin_cambiar_mayusculas():
    assert normalizar_direccion("  Calle  12   N° 345 ") == "Calle 12 N° 345"


def test_normalizar_direccion_vacia_devuelve_valor_nulo():
    assert normalizar_direccion("   ") is None


def test_normalizar_numero_acepta_coma_decimal():
    assert normalizar_numero("-34,91") == -34.91


def test_normalizar_numero_invalido_devuelve_valor_nulo():
    assert normalizar_numero("sin coordenada") is None
