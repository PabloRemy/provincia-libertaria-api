import os
from fastapi import FastAPI, Form, HTTPException
import psycopg2

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

@app.get("/")
def home():
    return {"status": "ok", "app": "Provincia Libertaria API"}

@app.post("/registro")
def crear_registro(
    nombre_apellido: str = Form(...),
    whatsapp: str = Form(...),
    email: str = Form(None),
    ciudad: str = Form(...),
    barrio: str = Form(None),
    participacion: str = Form(...),
    mensaje: str = Form(None),
):
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
            nombre_apellido,
            whatsapp,
            email,
            ciudad,
            barrio,
            participacion,
            mensaje
        ))

        nuevo_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()

        return {"ok": True, "id": nuevo_id}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
