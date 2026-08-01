import base64
from io import BytesIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi import HTTPException, UploadFile
from PIL import Image
from starlette.datastructures import Headers
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
    return UploadFile(
        file=BytesIO(contenido),
        filename=filename,
        headers=Headers({"content-type": content_type}),
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


@pytest.mark.parametrize("origen", ["upload", "base64"])
def test_error_de_pillow_elimina_archivo_parcial(tmp_path, monkeypatch, origen):
    import provincia_api.storage as storage

    entrada_upload = upload_falso()
    entrada_base64 = FotoBase64(content=imagen_png_base64())
    monkeypatch.setattr(storage, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(storage.uuid, "uuid4", lambda: SimpleNamespace(hex="parcial"))

    def guardar_parcial_y_fallar(self, file_path, format=None, **params):
        if hasattr(file_path, "write"):
            file_path.write(b"webp-incompleto")
            file_path.flush()
        else:
            Path(file_path).write_bytes(b"webp-incompleto")
        raise RuntimeError("fallo simulado de Pillow")

    monkeypatch.setattr(Image.Image, "save", guardar_parcial_y_fallar)

    with pytest.raises(HTTPException) as error:
        if origen == "upload":
            storage.procesar_foto_upload(entrada_upload)
        else:
            storage.procesar_foto_base64(entrada_base64)

    assert error.value.status_code == 400
    assert "fallo simulado de Pillow" in error.value.detail
    assert not (tmp_path / "parcial.webp").exists()


@pytest.mark.parametrize("origen", ["upload", "base64"])
def test_conversion_fija_parametros_webp(tmp_path, monkeypatch, origen):
    import provincia_api.storage as storage

    llamadas = []
    original_save = Image.Image.save
    entrada_upload = upload_falso()
    entrada_base64 = FotoBase64(content=imagen_png_base64())
    monkeypatch.setattr(storage, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(storage.uuid, "uuid4", lambda: SimpleNamespace(hex=origen))

    def registrar_save(self, file_path, format=None, **params):
        llamadas.append((format, params))
        return original_save(self, file_path, format, **params)

    monkeypatch.setattr(Image.Image, "save", registrar_save)

    if origen == "upload":
        storage.procesar_foto_upload(entrada_upload)
    else:
        storage.procesar_foto_base64(entrada_base64)

    assert llamadas == [
        (
            "WEBP",
            {"quality": 55, "method": 6, "optimize": True},
        )
    ]


@pytest.mark.parametrize("origen", ["upload", "base64"])
def test_error_no_elimina_destino_preexistente(tmp_path, monkeypatch, origen):
    import provincia_api.storage as storage

    destino = tmp_path / "existente.webp"
    destino.write_bytes(b"archivo-original")
    entrada_upload = upload_falso()
    entrada_base64 = FotoBase64(content=imagen_png_base64())
    monkeypatch.setattr(storage, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(storage.uuid, "uuid4", lambda: SimpleNamespace(hex="existente"))

    with pytest.raises(HTTPException):
        if origen == "upload":
            storage.procesar_foto_upload(entrada_upload)
        else:
            storage.procesar_foto_base64(entrada_base64)

    assert destino.read_bytes() == b"archivo-original"


@pytest.mark.parametrize("error_remove", [FileNotFoundError(), OSError("sin permiso")])
def test_error_de_limpieza_no_oculta_error_de_pillow(
    tmp_path,
    monkeypatch,
    error_remove,
):
    import provincia_api.storage as storage

    entrada = upload_falso()
    monkeypatch.setattr(storage, "UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr(storage.uuid, "uuid4", lambda: SimpleNamespace(hex="parcial"))

    def fallar_guardado(self, file_path, format=None, **params):
        raise RuntimeError("error original de Pillow")

    def fallar_eliminacion(file_path):
        raise error_remove

    monkeypatch.setattr(Image.Image, "save", fallar_guardado)
    monkeypatch.setattr(storage.os, "remove", fallar_eliminacion)

    with pytest.raises(HTTPException) as error:
        storage.procesar_foto_upload(entrada)

    assert error.value.status_code == 400
    assert "error original de Pillow" in error.value.detail
