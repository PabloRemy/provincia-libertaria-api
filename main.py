import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")


class Registro(BaseModel):
    nombre_apellido: str
    whatsapp: str
    email: Optional[str] = None
    ciudad: str
    barrio: Optional[str] = None
    participacion: str
    mensaje: Optional[str] = None


@app.get("/")
def home():
    return {"status": "ok", "app": "Provincia Libertaria API"}


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
