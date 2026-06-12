import os
import uuid
import base64
import json
import html
from io import BytesIO
from typing import Optional, List

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from pydantic import BaseModel
from PIL import Image
import psycopg2

app = FastAPI()

app.mount(
    "/uploads",
    StaticFiles(directory="/data/uploads"),
    name="uploads"
)

DATABASE_URL = os.getenv("DATABASE_URL")
UPLOAD_DIR = "/data/uploads/incidentes"
PUBLIC_UPLOAD_BASE = "/uploads/incidentes"

ESTADOS_VALIDOS = ["pendiente", "publicado", "resuelto", "oculto"]


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
    estado: Optional[str] = "pendiente"
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
    estado: Optional[str] = "pendiente"
    origen: Optional[str] = "vecino"
    fuente: Optional[str] = "formulario"
    latitud: Optional[float] = None
    longitud: Optional[float] = None


@app.get("/")
def home():
    return {"status": "ok", "app": "Provincia Libertaria API"}


def db_conn():
    if not DATABASE_URL:
        raise HTTPException(status_code=500, detail="DATABASE_URL no configurada")
    return psycopg2.connect(DATABASE_URL)


def ciudad_desde_slug(slug: str) -> str:
    mapa = {
        "berisso": "Berisso",
        "ensenada": "Ensenada",
        "la-plata": "La Plata",
        "punta-indio": "Punta Indio",
        "magdalena": "Magdalena",
        "quilmes": "Quilmes",
        "avellaneda": "Avellaneda",
        "lanus": "Lanús",
        "lomas-de-zamora": "Lomas de Zamora",
        "almirante-brown": "Almirante Brown",
        "florencio-varela": "Florencio Varela",
        "berazategui": "Berazategui",
        "esteban-echeverria": "Esteban Echeverría",
        "ezeiza": "Ezeiza",
        "canuelas": "Cañuelas",
        "san-vicente": "San Vicente",
        "presidente-peron": "Presidente Perón",
        "la-matanza": "La Matanza"
    }

    return mapa.get(slug.lower(), slug.replace("-", " ").title())


def insertar_incidente(
    ciudad,
    barrio,
    categoria,
    descripcion,
    foto_url=None,
    estado="pendiente",
    origen="vecino",
    fuente="formulario",
    latitud=None,
    longitud=None,
):
    conn = db_conn()
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


@app.get("/foto/{nombre}")
def ver_foto(nombre: str):
    if "/" in nombre or ".." in nombre:
        raise HTTPException(status_code=400, detail="Nombre de archivo inválido")

    file_path = os.path.join(UPLOAD_DIR, nombre)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Foto no encontrada")

    return FileResponse(file_path, media_type="image/webp")


@app.post("/registro")
def crear_registro(registro: Registro):
    try:
        conn = db_conn()
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
            estado=incidente.estado or "pendiente",
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
            estado=incidente.estado or "pendiente",
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


@app.post("/incidentes/estado-lote")
def cambiar_estado_lote(
    ids: List[int] = Form(default=[]),
    estado: str = Form(...),
    volver: str = Form("/territorio/berisso")
):
    actualizar_estado_incidentes(ids, estado)
    return RedirectResponse(url=volver, status_code=303)


@app.get("/panel/berisso")
def redirigir_panel_berisso():
    return RedirectResponse(url="/territorio/berisso", status_code=301)


@app.get("/territorio/{distrito_slug}", response_class=HTMLResponse)
def panel_distrito(distrito_slug: str, estado: str = "pendiente"):
    ciudad = ciudad_desde_slug(distrito_slug)

    if estado not in ESTADOS_VALIDOS and estado != "todos":
        estado = "pendiente"

    conn = db_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM reclutamiento_registros
        WHERE LOWER(ciudad) = LOWER(%s);
    """, (ciudad,))
    adhesiones = cur.fetchone()[0]

    cur.execute("""
        SELECT estado, COUNT(*)
        FROM incidentes
        WHERE LOWER(ciudad) = LOWER(%s)
        GROUP BY estado;
    """, (ciudad,))
    estados_data = dict(cur.fetchall())

    pendientes = estados_data.get("pendiente", 0)
    publicados = estados_data.get("publicado", 0)
    resueltos = estados_data.get("resuelto", 0)
    ocultos = estados_data.get("oculto", 0)

    cur.execute("""
        SELECT barrio, COUNT(*) AS total
        FROM incidentes
        WHERE LOWER(ciudad) = LOWER(%s)
        GROUP BY barrio
        ORDER BY total DESC;
    """, (ciudad,))
    barrios = cur.fetchall()

    barrios_activos = len(barrios)

    if estado == "todos":
        cur.execute("""
            SELECT id, barrio, categoria, descripcion, foto_url, fecha_reporte, estado
            FROM incidentes
            WHERE LOWER(ciudad) = LOWER(%s)
            ORDER BY fecha_reporte DESC
            LIMIT 24;
        """, (ciudad,))
    else:
        cur.execute("""
            SELECT id, barrio, categoria, descripcion, foto_url, fecha_reporte, estado
            FROM incidentes
            WHERE LOWER(ciudad) = LOWER(%s)
              AND estado = %s
            ORDER BY fecha_reporte DESC
            LIMIT 24;
        """, (ciudad, estado))

    incidentes = cur.fetchall()

    if estado == "todos":
        cur.execute("""
            SELECT categoria, COUNT(*) AS total
            FROM incidentes
            WHERE LOWER(ciudad) = LOWER(%s)
            GROUP BY categoria
            ORDER BY total DESC;
        """, (ciudad,))
    else:
        cur.execute("""
            SELECT categoria, COUNT(*) AS total
            FROM incidentes
            WHERE LOWER(ciudad) = LOWER(%s)
              AND estado = %s
            GROUP BY categoria
            ORDER BY total DESC;
        """, (ciudad, estado))

    categorias = cur.fetchall()

    cur.close()
    conn.close()

    cards_html = ""

    for item in incidentes:
        id_incidente, barrio, categoria, descripcion, foto_url, fecha, estado_actual = item

        barrio_safe = html.escape(barrio or "")
        categoria_safe = html.escape(categoria or "")
        descripcion_safe = html.escape(descripcion or "")
        estado_safe = html.escape(estado_actual or "")

        if foto_url:
            nombre_foto = foto_url.split("/")[-1]
            imagen_html = f'<img src="/foto/{html.escape(nombre_foto)}" alt="Foto del reporte">'
        else:
            imagen_html = '<div class="sin-foto">Sin foto</div>'

        cards_html += f"""
        <article class="card">
            <label class="check">
                <input type="checkbox" name="ids" value="{id_incidente}">
                Seleccionar
            </label>

            <div class="thumb">{imagen_html}</div>

            <div class="contenido">
                <div class="meta">#{id_incidente} · {fecha.strftime('%d/%m/%Y %H:%M')}</div>
                <div class="estado estado-{estado_safe}">{estado_safe}</div>
                <h3>{categoria_safe}</h3>
                <p class="barrio">{barrio_safe}</p>
                <p>{descripcion_safe}</p>
            </div>
        </article>
        """

    categorias_html = ""

    for categoria, total in categorias:
        categorias_html += f"""
        <li>
            <span>{html.escape(categoria)}</span>
            <strong>{total}</strong>
        </li>
        """

    barrios_html = ""

    for barrio, total in barrios:
        barrios_html += f"""
        <li>
            <span>{html.escape(barrio or "Sin barrio")}</span>
            <strong>{total}</strong>
        </li>
        """

    if not cards_html:
        cards_html = '<p class="vacio">No hay reportes en esta vista.</p>'

    if not categorias_html:
        categorias_html = '<li><span>Sin datos</span><strong>0</strong></li>'

    if not barrios_html:
        barrios_html = '<li><span>Sin barrios activos</span><strong>0</strong></li>'

    def active(e):
        return "active" if estado == e else ""

    html_response = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Territorio {html.escape(ciudad)} - Provincia Libertaria</title>
        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #48020c;
                color: #ffffff;
            }}

            .wrap {{
                max-width: 1180px;
                margin: 0 auto;
                padding: 32px 18px;
            }}

            .eyebrow {{
                color: #f1d571;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: .08em;
                font-size: 13px;
            }}

            h1 {{
                margin: 8px 0 6px;
                font-size: 38px;
                color: #f1d571;
            }}

            .sub {{
                margin: 0;
                color: #f7e7b0;
            }}

            .public-link {{
                display: inline-block;
                margin-top: 14px;
                color: #f1d571;
                border: 1px solid #b98b31;
                padding: 8px 12px;
                border-radius: 999px;
                text-decoration: none;
                font-weight: 700;
            }}

            .stats {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 14px;
                margin: 28px 0;
            }}

            .stat {{
                background: #650713;
                border: 1px solid #b98b31;
                border-radius: 12px;
                padding: 18px;
            }}

            .stat span {{
                display: block;
                font-size: 13px;
                color: #f1d571;
                margin-bottom: 8px;
            }}

            .stat strong {{
                font-size: 28px;
            }}

            .tabs {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin: 22px 0;
            }}

            .tabs a {{
                color: #f1d571;
                border: 1px solid #b98b31;
                padding: 10px 14px;
                border-radius: 999px;
                text-decoration: none;
                font-weight: 700;
            }}

            .tabs a.active {{
                background: #b98b31;
                color: #121212;
            }}

            .toolbar {{
                background: #650713;
                border: 1px solid #b98b31;
                border-radius: 12px;
                padding: 14px;
                margin: 18px 0;
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                align-items: center;
            }}

            .toolbar button {{
                border: 0;
                border-radius: 6px;
                padding: 10px 14px;
                font-weight: 700;
                cursor: pointer;
            }}

            .btn-publicar {{
                background: #f1d571;
                color: #121212;
            }}

            .btn-resuelto {{
                background: #24a148;
                color: #ffffff;
            }}

            .btn-oculto {{
                background: #121212;
                color: #ffffff;
            }}

            .btn-pendiente {{
                background: #9d1018;
                color: #ffffff;
            }}

            .grid {{
                display: grid;
                grid-template-columns: 1fr 320px;
                gap: 20px;
                align-items: start;
            }}

            .cards {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 16px;
            }}

            .card {{
                background: #ffffff;
                color: #121212;
                border-radius: 14px;
                overflow: hidden;
                border: 1px solid #b98b31;
                position: relative;
            }}

            .check {{
                display: block;
                padding: 10px 12px;
                background: #f7f1df;
                font-size: 13px;
                font-weight: 700;
            }}

            .thumb {{
                width: 100%;
                height: 180px;
                background: #240106;
            }}

            .thumb img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                display: block;
            }}

            .sin-foto {{
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #f1d571;
                font-weight: 700;
            }}

            .contenido {{
                padding: 16px;
            }}

            .meta {{
                color: #777;
                font-size: 12px;
                margin-bottom: 8px;
            }}

            .estado {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 999px;
                font-size: 12px;
                font-weight: 700;
                margin-bottom: 8px;
            }}

            .estado-pendiente {{
                background: #f1d571;
                color: #121212;
            }}

            .estado-publicado {{
                background: #dff5df;
                color: #145214;
            }}

            .estado-resuelto {{
                background: #e8f0ff;
                color: #123f7a;
            }}

            .estado-oculto {{
                background: #222;
                color: #fff;
            }}

            .card h3 {{
                margin: 0 0 6px;
                color: #9d1018;
                font-size: 20px;
            }}

            .barrio {{
                margin: 0 0 10px;
                font-weight: 700;
            }}

            .side {{
                display: grid;
                gap: 16px;
            }}

            .box {{
                background: #650713;
                border: 1px solid #b98b31;
                border-radius: 14px;
                padding: 18px;
            }}

            .box h2 {{
                margin-top: 0;
                color: #f1d571;
                font-size: 22px;
            }}

            .box ul {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}

            .box li {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid rgba(241,213,113,.25);
            }}

            .box li:last-child {{
                border-bottom: 0;
            }}

            .vacio {{
                color: #f1d571;
                font-weight: 700;
            }}

            @media (max-width: 850px) {{
                .stats {{
                    grid-template-columns: repeat(2, 1fr);
                }}

                .grid {{
                    grid-template-columns: 1fr;
                }}

                .cards {{
                    grid-template-columns: 1fr;
                }}

                h1 {{
                    font-size: 32px;
                }}
            }}
        </style>
    </head>
    <body>
        <main class="wrap">
            <section>
                <div class="eyebrow">Panel territorial</div>
                <h1>Distrito {html.escape(ciudad)}</h1>
                <p class="sub">Adhesiones, reportes y moderación territorial.</p>
                <a class="public-link" href="/reportes/{html.escape(distrito_slug)}">Ver página pública</a>
            </section>

            <section class="stats">
                <div class="stat">
                    <span>Adhesiones</span>
                    <strong>{adhesiones}</strong>
                </div>
                <div class="stat">
                    <span>Pendientes</span>
                    <strong>{pendientes}</strong>
                </div>
                <div class="stat">
                    <span>Publicados</span>
                    <strong>{publicados}</strong>
                </div>
                <div class="stat">
                    <span>Barrios activos</span>
                    <strong>{barrios_activos}</strong>
                </div>
            </section>

            <nav class="tabs">
                <a class="{active('pendiente')}" href="/territorio/{html.escape(distrito_slug)}?estado=pendiente">Pendientes ({pendientes})</a>
                <a class="{active('publicado')}" href="/territorio/{html.escape(distrito_slug)}?estado=publicado">Publicados ({publicados})</a>
                <a class="{active('resuelto')}" href="/territorio/{html.escape(distrito_slug)}?estado=resuelto">Resueltos ({resueltos})</a>
                <a class="{active('oculto')}" href="/territorio/{html.escape(distrito_slug)}?estado=oculto">Ocultos ({ocultos})</a>
                <a class="{active('todos')}" href="/territorio/{html.escape(distrito_slug)}?estado=todos">Todos</a>
            </nav>

            <form method="post" action="/incidentes/estado-lote">
                <input type="hidden" name="volver" value="/territorio/{html.escape(distrito_slug)}?estado={html.escape(estado)}">

                <div class="toolbar">
                    <strong>Acción sobre seleccionados:</strong>
                    <button class="btn-publicar" type="submit" name="estado" value="publicado">Aprobar / Publicar</button>
                    <button class="btn-resuelto" type="submit" name="estado" value="resuelto">Marcar resuelto</button>
                    <button class="btn-oculto" type="submit" name="estado" value="oculto">Ocultar</button>
                    <button class="btn-pendiente" type="submit" name="estado" value="pendiente">Volver a pendiente</button>
                </div>

                <section class="grid">
                    <div>
                        <h2>Reportes: {html.escape(estado)}</h2>
                        <div class="cards">
                            {cards_html}
                        </div>
                    </div>

                    <aside class="side">
                        <div class="box">
                            <h2>Barrios</h2>
                            <ul>
                                {barrios_html}
                            </ul>
                        </div>

                        <div class="box">
                            <h2>Categorías</h2>
                            <ul>
                                {categorias_html}
                            </ul>
                        </div>
                    </aside>
                </section>
            </form>
        </main>
    </body>
    </html>
    """

    return HTMLResponse(content=html_response)


@app.get("/reportes/{distrito_slug}", response_class=HTMLResponse)
def reportes_publicos(distrito_slug: str):
    ciudad = ciudad_desde_slug(distrito_slug)

    conn = db_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, barrio, categoria, descripcion, foto_url, fecha_reporte
        FROM incidentes
        WHERE LOWER(ciudad) = LOWER(%s)
          AND estado = 'publicado'
        ORDER BY fecha_reporte DESC
        LIMIT 24;
    """, (ciudad,))

    incidentes = cur.fetchall()

    cur.close()
    conn.close()

    cards_html = ""

    for item in incidentes:
        id_incidente, barrio, categoria, descripcion, foto_url, fecha = item

        barrio_safe = html.escape(barrio or "")
        categoria_safe = html.escape(categoria or "")
        descripcion_safe = html.escape(descripcion or "")

        if foto_url:
            nombre_foto = foto_url.split("/")[-1]
            imagen_html = f'<img src="/foto/{html.escape(nombre_foto)}" alt="Foto del reporte">'
        else:
            imagen_html = '<div class="sin-foto">Sin foto</div>'

        cards_html += f"""
        <article class="card">
            <div class="thumb">{imagen_html}</div>
            <div class="contenido">
                <div class="meta">#{id_incidente} · {fecha.strftime('%d/%m/%Y %H:%M')}</div>
                <h3>{categoria_safe}</h3>
                <p class="barrio">{barrio_safe}</p>
                <p>{descripcion_safe}</p>
            </div>
        </article>
        """

    if not cards_html:
        cards_html = '<p class="vacio">Todavía no hay reportes publicados para este distrito.</p>'

    html_response = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reportes {html.escape(ciudad)} - Provincia Libertaria</title>
        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #48020c;
                color: #ffffff;
            }}

            .wrap {{
                max-width: 1180px;
                margin: 0 auto;
                padding: 32px 18px;
            }}

            .eyebrow {{
                color: #f1d571;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: .08em;
                font-size: 13px;
            }}

            h1 {{
                margin: 8px 0 6px;
                font-size: 38px;
                color: #f1d571;
            }}

            .sub {{
                margin: 0 0 28px;
                color: #f7e7b0;
            }}

            .cards {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
            }}

            .card {{
                background: #ffffff;
                color: #121212;
                border-radius: 14px;
                overflow: hidden;
                border: 1px solid #b98b31;
            }}

            .thumb {{
                width: 100%;
                height: 180px;
                background: #240106;
            }}

            .thumb img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                display: block;
            }}

            .sin-foto {{
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: #f1d571;
                font-weight: 700;
            }}

            .contenido {{
                padding: 16px;
            }}

            .meta {{
                color: #777;
                font-size: 12px;
                margin-bottom: 8px;
            }}

            .card h3 {{
                margin: 0 0 6px;
                color: #9d1018;
                font-size: 20px;
            }}

            .barrio {{
                margin: 0 0 10px;
                font-weight: 700;
            }}

            .vacio {{
                color: #f1d571;
                font-weight: 700;
            }}

            @media (max-width: 850px) {{
                .cards {{
                    grid-template-columns: 1fr;
                }}

                h1 {{
                    font-size: 32px;
                }}
            }}
        </style>
    </head>
    <body>
        <main class="wrap">
            <section>
                <div class="eyebrow">Mapa de Barrio</div>
                <h1>Reportes de {html.escape(ciudad)}</h1>
                <p class="sub">Problemas publicados y verificados por referentes territoriales.</p>
            </section>

            <section class="cards">
                {cards_html}
            </section>
        </main>
    </body>
    </html>
    """

    return HTMLResponse(content=html_response)


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
