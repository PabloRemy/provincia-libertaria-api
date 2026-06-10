import os
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from PIL import Image
import psycopg2

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


def procesar_foto(foto: UploadFile) -> Optional[str]:
    if not foto or not foto.filename:
        return None

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    extension_permitida = foto.content_type in [
        "image/jpeg",
        "image/png",
        "image/webp"
    ]

    if not extension_permitida:
        raise HTTPException(status_code=400, detail="Formato de imagen no permitido")

    filename = f"{uuid.uuid4().hex}.webp"
    file_path = os.path.join(UPLOAD_DIR, filename)

    try:
        image = Image.open(foto.file)
        image = image.convert("RGB")

        image.thumbnail((800, 800))

        image.save(
            file_path,
            "WEBP",
            quality=55,
            method=6,
            optimize=True
        )

        return f"{PUBLIC_UPLOAD_BASE}/{filename}"

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"No se pudo procesar la imagen: {str(e)}")


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
        foto_url = procesar_foto(foto) if foto else None

        nuevo_id = insertar_incidente(
            ciudad=ciudad,
            barrio=barrio,
            categoria=categoria,
            descripcion=descripcion,
            foto_url=foto_url,
            origen=origen,
            fuente=fuente,
        )

        return {
            "ok": True,
            "id": nuevo_id,
            "foto_url": foto_url
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
