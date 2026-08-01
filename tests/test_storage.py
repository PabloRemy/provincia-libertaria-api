import base64
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from PIL import Image
from starlette.staticfiles import StaticFiles

from provincia_api.models import FotoBase64


original_static_files_init = StaticFiles.__init__


def init_static_files_without_directory_check(self, *args, **kwargs):
    kwargs["check_dir"] = False
    original_static_files_init(self, *args, **kwargs)


def imagen_png_base64(size=(1200, 600)):
    buffer = BytesIO()
    Image.new("RGB", size, color=(210, 180, 140)).save(buffer, "PNG")
    return base64.b64encode(buffer.getvalue()).decode("ascii")


def upload_falso(*, content_type="image/png", filename="foto.png", size=(1200, 600)):
    contenido = base64.b64decode(imagen_png_base64(size))
    return SimpleNamespace(
        content_type=content_type,
        filename=filename,
        file=BytesIO(contenido),
    )


def test_main_reexporta_helpers_de_almacenamiento():
    from provincia_api.storage import (
        procesar_foto_base64,
        procesar_foto_upload,
        procesar_foto_webhook,
        url_publica_foto,
    )

    with patch.object(StaticFiles, "__init__", init_static_files_without_directory_check):
        import main

    assert main.procesar_foto_upload is procesar_foto_upload
    assert main.procesar_foto_base64 is procesar_foto_base64
    assert main.procesar_foto_webhook is procesar_foto_webhook
    assert main.url_publica_foto is url_publica_foto


def test_upload_vacio_no_crea_archivo(tmp_path, monkeypatch):
    import provincia_api.storage as storage

    monkeypatch.setattr(storage, "UPLOAD_DIR", str(tmp_path))

    assert storage.procesar_foto_upload(None) is None
    assert storage.procesar_foto_upload(upload_falso(filename="")) is None
    assert list(tmp_path.iterdir()) == []


def test_upload_rechaza_mime_no_permitido(tmp_path, monkeypatch):
    import provincia_api.storage as storage

    monkeypatch.setattr(storage, "UPLOAD_DIR", str(tmp_path))

    with pytest.raises(HTTPException) as error:
        storage.procesar_foto_upload(upload_falso(content_type="image/gif"))

    assert error.value.status_code == 400
    assert error.value.detail == "Formato de imagen no permitido"


def test_upload_convierte_a_webp_y_limita_dimensiones(tmp_path, monkeypatch):
    import provincia_api.storage as storage

    monkeypatch.setattr(storage, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(storage.uuid, "uuid4", lambda: SimpleNamespace(hex="upload-fijo"))

    result = storage.procesar_foto_upload(upload_falso())
    destino = tmp_path / "upload-fijo.webp"

    assert result == "/uploads/incidentes/upload-fijo.webp"
    assert destino.exists()
    with Image.open(destino) as image:
        assert image.format == "WEBP"
        assert image.size == (800, 400)


def test_base64_convierte_a_webp(tmp_path, monkeypatch):
    import provincia_api.storage as storage

    monkeypatch.setattr(storage, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(storage.uuid, "uuid4", lambda: SimpleNamespace(hex="base64-fijo"))

    result = storage.procesar_foto_base64(FotoBase64(content=imagen_png_base64((400, 300))))
    destino = tmp_path / "base64-fijo.webp"

    assert result == "/uploads/incidentes/base64-fijo.webp"
    assert destino.exists()
    with Image.open(destino) as image:
        assert image.format == "WEBP"
        assert image.size == (400, 300)


def test_base64_invalido_devuelve_error_http(tmp_path, monkeypatch):
    import provincia_api.storage as storage

    monkeypatch.setattr(storage, "UPLOAD_DIR", str(tmp_path))

    with pytest.raises(HTTPException) as error:
        storage.procesar_foto_base64(FotoBase64(content="no-es-una-imagen"))

    assert error.value.status_code == 400
    assert error.value.detail.startswith("No se pudo procesar la imagen base64:")


def test_webhook_acepta_objeto_base64_y_urls_http(monkeypatch):
    import provincia_api.storage as storage

    monkeypatch.setattr(
        storage,
        "procesar_foto_base64",
        lambda foto: f"procesada:{foto.filename}",
    )

    foto = FotoBase64(filename="foto.png", content="contenido")
    assert storage.procesar_foto_webhook(foto) == "procesada:foto.png"
    assert storage.procesar_foto_webhook(foto.model_dump()) == "procesada:foto.png"
    assert storage.procesar_foto_webhook("https://ejemplo.test/foto.jpg") == (
        "https://ejemplo.test/foto.jpg"
    )


def test_webhook_rechaza_rutas_locales_y_url_publica_resuelve_archivos():
    from provincia_api.storage import procesar_foto_webhook, url_publica_foto

    with pytest.raises(HTTPException) as error:
        procesar_foto_webhook("/tmp/foto.jpg")

    assert error.value.status_code == 400
    assert error.value.detail == "URL de foto inválida"
    assert url_publica_foto(None) is None
    assert url_publica_foto("https://ejemplo.test/foto.jpg") == (
        "https://ejemplo.test/foto.jpg"
    )
    assert url_publica_foto("/uploads/incidentes/local.webp") == "/foto/local.webp"
