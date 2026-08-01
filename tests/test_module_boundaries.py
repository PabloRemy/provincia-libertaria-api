from unittest.mock import patch

from starlette.staticfiles import StaticFiles


original_static_files_init = StaticFiles.__init__


def init_static_files_without_directory_check(self, *args, **kwargs):
    kwargs["check_dir"] = False
    original_static_files_init(self, *args, **kwargs)


def test_main_reexporta_simbolos_extraidos():
    from provincia_api.auth import (
        get_current_admin,
        parse_admin_users,
        puede_ver_distrito,
        requiere_distrito,
        security,
    )
    from provincia_api.config import (
        DATA_DIR,
        DISTRITOS_TERCERA,
        ESTADOS_VALIDOS,
        PUBLIC_UPLOAD_BASE,
        UPLOAD_DIR,
        UPLOAD_ROOT,
    )
    from provincia_api.normalization import (
        ciudad_desde_slug,
        normalizar_direccion,
        normalizar_numero,
        normalizar_texto,
        slug_desde_ciudad,
    )

    with patch.object(StaticFiles, "__init__", init_static_files_without_directory_check):
        import main

    assert main.DATA_DIR == DATA_DIR
    assert main.UPLOAD_ROOT == UPLOAD_ROOT
    assert main.UPLOAD_DIR == UPLOAD_DIR
    assert main.PUBLIC_UPLOAD_BASE == PUBLIC_UPLOAD_BASE
    assert main.ESTADOS_VALIDOS is ESTADOS_VALIDOS
    assert main.DISTRITOS_TERCERA is DISTRITOS_TERCERA
    assert main.parse_admin_users is parse_admin_users
    assert main.get_current_admin is get_current_admin
    assert main.puede_ver_distrito is puede_ver_distrito
    assert main.requiere_distrito is requiere_distrito
    assert main.security is security
    assert main.normalizar_texto is normalizar_texto
    assert main.normalizar_direccion is normalizar_direccion
    assert main.normalizar_numero is normalizar_numero
    assert main.slug_desde_ciudad is slug_desde_ciudad
    assert main.ciudad_desde_slug is ciudad_desde_slug


def test_main_reexporta_modelos_extraidos():
    from provincia_api.models import (
        FotoBase64,
        Incidente,
        IncidenteFotoJSON,
        Registro,
    )

    with patch.object(StaticFiles, "__init__", init_static_files_without_directory_check):
        import main

    assert main.Registro is Registro
    assert main.Incidente is Incidente
    assert main.FotoBase64 is FotoBase64
    assert main.IncidenteFotoJSON is IncidenteFotoJSON
