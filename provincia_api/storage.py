import base64
from io import BytesIO
import os
from typing import Optional, Union
from urllib.parse import urlparse
import uuid

from fastapi import HTTPException, UploadFile
from PIL import Image

from provincia_api.config import PUBLIC_UPLOAD_BASE, UPLOAD_DIR
from provincia_api.models import FotoBase64


def procesar_foto_upload(foto: UploadFile) -> Optional[str]:
    if not foto or not foto.filename:
        return None

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    if foto.content_type not in ["image/jpeg", "image/png", "image/webp"]:
        raise HTTPException(status_code=400, detail="Formato de imagen no permitido")

    filename = f"{uuid.uuid4().hex}.webp"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        image = Image.open(foto.file)
        image = image.convert("RGB")
        image.thumbnail((800, 800))
        image.save(file_path, "WEBP", quality=55, method=6, optimize=True)

        return f"{PUBLIC_UPLOAD_BASE}/{filename}"

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo procesar la imagen: {str(e)}")


def procesar_foto_base64(foto: FotoBase64) -> Optional[str]:
    if not foto or not foto.content:
        return None

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.webp"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        image_bytes = base64.b64decode(foto.content)
        image = Image.open(BytesIO(image_bytes))
        image = image.convert("RGB")
        image.thumbnail((800, 800))
        image.save(file_path, "WEBP", quality=55, method=6, optimize=True)

        return f"{PUBLIC_UPLOAD_BASE}/{filename}"

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo procesar la imagen base64: {str(e)}")


def procesar_foto_webhook(foto: Optional[Union[FotoBase64, str]]) -> Optional[str]:
    if foto is None:
        return None

    if isinstance(foto, dict):
        return procesar_foto_base64(FotoBase64.model_validate(foto))

    if isinstance(foto, FotoBase64):
        return procesar_foto_base64(foto)

    foto_url = foto.strip()
    if not foto_url:
        return None

    parsed = urlparse(foto_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        raise HTTPException(status_code=400, detail="URL de foto inválida")

    return foto_url


def url_publica_foto(foto_url: Optional[str]) -> Optional[str]:
    if not foto_url:
        return None

    parsed = urlparse(foto_url)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return foto_url

    return f"/foto/{foto_url.split('/')[-1]}"
