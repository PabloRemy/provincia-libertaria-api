import os
from typing import List

from fastapi import HTTPException
import psycopg2

from provincia_api.config import ESTADOS_VALIDOS
from provincia_api.normalization import normalizar_direccion, normalizar_texto


def db_conn():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL no configurada")
    return psycopg2.connect(database_url)


def insertar_incidente(
    ciudad,
    barrio,
    categoria,
    descripcion,
    categoria_detalle=None,
    direccion=None,
    foto_url=None,
    estado="pendiente",
    origen="vecino",
    fuente="formulario",
    latitud=None,
    longitud=None,
):
    ciudad = normalizar_texto(ciudad)
    barrio = normalizar_texto(barrio)
    categoria = normalizar_texto(categoria)
    categoria_detalle = normalizar_direccion(categoria_detalle)
    direccion = normalizar_direccion(direccion)

    conn = db_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO incidentes
        (ciudad, barrio, categoria, categoria_detalle, descripcion, direccion, foto_url, estado, origen, fuente, latitud, longitud)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """, (
        ciudad,
        barrio,
        categoria,
        categoria_detalle,
        descripcion,
        direccion,
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


def actualizar_estado_incidentes(ids: List[int], estado: str):
    if estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Estado inválido")

    if not ids:
        return 0

    conn = db_conn()
    cur = conn.cursor()

    cur.execute("""
        UPDATE incidentes
        SET estado = %s,
            fecha_actualizacion = NOW()
        WHERE id = ANY(%s);
    """, (estado, ids))

    afectados = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()

    return afectados
