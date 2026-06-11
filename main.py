import os
import uuid
import base64
from io import BytesIO
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image
import psycopg2
import json

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")
UPLOAD_DIR = "/data/uploads/incidentes"
PUBLIC_UPLOAD_BASE = "/uploads/incidentes"


class Registro(BaseModel):
    nombre_apellido: str
    whatsapp: str
    email: Optional[str] = None
    ciudad: str
    barrio: Optional[str] = None
    participacion: str
    mensaje: Optional[str] = None


class Incidente(BaseModel):
    ciudad: str
    barrio: str
    categoria: str
    descripcion: str
    foto_url: Optional[str] = None
    estado: Optional[str] = "nuevo"
    origen: Optional[str] = "vecino"
    fuente: Optional[str] = "formulario"
    latitud: Optional[float] = None
    longitud: Optional[float] = None


class FotoBase64(BaseModel):
    filename: Optional[str] = None
    content: str


class IncidenteFotoJSON(BaseModel):
    ciudad: str
    barrio: str
    categoria: str
    descripcion: str
    foto: Optional[FotoBase64] = None
    estado: Optional[str] = "nuevo"
    origen: Optional[str] = "vecino"
    fuente: Optional[str] = "formulario"
    latitud: Optional[float] = None
    longitud: Optional[float] = None


@app.get("/")
def home():
    return {"status": "ok", "app": "Provincia Libertaria API"}


def insertar_incidente(
    ciudad,
    barrio,
    categoria,
    descripcion,
    foto_url=None,
    estado="nuevo",
    origen="vecino",
    fuente="formulario",
    latitud=None,
    longitud=None,
):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no configurada")

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO incidentes
        (ciudad, barrio, categoria, descripcion, foto_url, estado, origen, fuente, latitud, longitud)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        ciudad,
        barrio,
        categoria,
        descripcion,
        foto_url,
        estado,
        origen,
        fuente,
        latitud,
        longitud
    ))

    nuevo_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return nuevo_id


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


@app.post("/registro")
def crear_registro(registro: Registro):
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no configurada")

    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO reclutamiento_registros
            (nombre_apellido, whatsapp, email, ciudad, barrio, participacion, mensaje)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            registro.nombre_apellido,
            registro.whatsapp,
            registro.email,
            registro.ciudad,
            registro.barrio,
            registro.participacion,
            registro.mensaje
        ))

        nuevo_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return {"ok": True, "id": nuevo_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/incidente")
def crear_incidente(incidente: Incidente):
    try:
        nuevo_id = insertar_incidente(
            ciudad=incidente.ciudad,
            barrio=incidente.barrio,
            categoria=incidente.categoria,
            descripcion=incidente.descripcion,
            foto_url=incidente.foto_url,
            estado=incidente.estado,
            origen=incidente.origen,
            fuente=incidente.fuente,
            latitud=incidente.latitud,
            longitud=incidente.longitud,
        )

        return {"ok": True, "id": nuevo_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/incidente-foto")
def crear_incidente_con_foto(
    ciudad: str = Form(...),
    barrio: str = Form(...),
    categoria: str = Form(...),
    descripcion: str = Form(...),
    origen: str = Form("vecino"),
    fuente: str = Form("formulario"),
    foto: Optional[UploadFile] = File(None),
):
    try:
        foto_url = procesar_foto_upload(foto) if foto else None

        nuevo_id = insertar_incidente(
            ciudad=ciudad,
            barrio=barrio,
            categoria=categoria,
            descripcion=descripcion,
            foto_url=foto_url,
            origen=origen,
            fuente=fuente,
        )

        return {"ok": True, "id": nuevo_id, "foto_url": foto_url}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/incidente-foto-json")
def crear_incidente_con_foto_json(incidente: IncidenteFotoJSON):
    try:
        foto_url = procesar_foto_base64(incidente.foto) if incidente.foto else None

        nuevo_id = insertar_incidente(
            ciudad=incidente.ciudad,
            barrio=incidente.barrio,
            categoria=incidente.categoria,
            descripcion=incidente.descripcion,
            foto_url=foto_url,
            estado=incidente.estado,
            origen=incidente.origen,
            fuente=incidente.fuente,
            latitud=incidente.latitud,
            longitud=incidente.longitud,
        )

        return {"ok": True, "id": nuevo_id, "foto_url": foto_url}

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/debug")
async def debug_request(request: Request):
    content_type = request.headers.get("content-type", "")
    print("DEBUG CONTENT-TYPE:", content_type, flush=True)

    if "application/json" in content_type:
        data = await request.json()
        print("DEBUG JSON:", json.dumps(data, ensure_ascii=False)[:3000], flush=True)
        return {"ok": True, "type": "json"}

    form = await request.form()
    form_data = {key: str(value)[:500] for key, value in form.items()}
    print("DEBUG FORM KEYS:", list(form.keys()), flush=True)
    print("DEBUG FORM DATA:", json.dumps(form_data, ensure_ascii=False)[:3000], flush=True)

    return {"ok": True, "type": "form", "keys": list(form.keys())}
