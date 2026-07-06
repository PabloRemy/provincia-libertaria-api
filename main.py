import os
import uuid
import base64
import json
import html
import secrets
from io import BytesIO
from typing import Optional, List, Union, Any
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel
from PIL import Image
import psycopg2

app = FastAPI()

DATA_DIR = os.getenv("DATA_DIR", "/data")
UPLOAD_ROOT = os.path.join(DATA_DIR, "uploads")

app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_ROOT, check_dir=False),
    name="uploads"
)

UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "incidentes")
PUBLIC_UPLOAD_BASE = "/uploads/incidentes"

ESTADOS_VALIDOS = ["pendiente", "publicado", "resuelto", "oculto"]

security = HTTPBasic()

DISTRITOS_TERCERA = [
    ("berisso", "Berisso"),
    ("ensenada", "Ensenada"),
    ("la-plata", "La Plata"),
]

def parse_admin_users():
    raw = os.getenv("ADMIN_USERS", "")
    users = {}

    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue

        parts = item.split(":")
        if len(parts) != 3:
            continue

        username, password, scope = parts
        users[username.strip()] = {
            "password": password.strip(),
            "scope": scope.strip()
        }

    return users


def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)):
    users = parse_admin_users()

    if not users:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_USERS no configurado"
        )

    user_data = users.get(credentials.username)

    valid_user = user_data is not None
    valid_password = (
        valid_user and
        secrets.compare_digest(credentials.password, user_data["password"])
    )

    if not valid_user or not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña inválidos",
            headers={"WWW-Authenticate": "Basic"},
        )

    return {
        "username": credentials.username,
        "scope": user_data["scope"]
    }


def puede_ver_distrito(admin, distrito_slug: str) -> bool:
    scope = admin.get("scope")

    if scope == "todos":
        return True

    if scope == "tercera-seccion":
        return distrito_slug in [slug for slug, _ in DISTRITOS_TERCERA]

    return scope == distrito_slug


def requiere_distrito(distrito_slug: str, admin):
    if not puede_ver_distrito(admin, distrito_slug):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para ver este distrito"
        )


def slug_desde_ciudad(ciudad: Optional[str]) -> str:
    if not ciudad:
        return "berisso"

    ciudad_norm = normalizar_texto(ciudad) or ""

    mapa = {
        "Berisso": "berisso",
        "Ensenada": "ensenada",
        "La Plata": "la-plata",
        "Punta Indio": "punta-indio",
        "Magdalena": "magdalena",
        "Quilmes": "quilmes",
        "Avellaneda": "avellaneda",
        "Lanús": "lanus",
        "Lomas De Zamora": "lomas-de-zamora",
        "Almirante Brown": "almirante-brown",
        "Florencio Varela": "florencio-varela",
        "Berazategui": "berazategui",
        "Esteban Echeverría": "esteban-echeverria",
        "Ezeiza": "ezeiza",
        "Cañuelas": "canuelas",
        "San Vicente": "san-vicente",
        "Presidente Perón": "presidente-peron",
        "La Matanza": "la-matanza",
    }

    return mapa.get(ciudad_norm, ciudad_norm.lower().replace(" ", "-"))



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
    categoria_detalle: Optional[str] = None
    descripcion: str
    direccion: Optional[str] = None
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
    barrio: Optional[str] = None
    categoria: str
    categoria_detalle: Optional[str] = None
    descripcion: str
    direccion: Optional[str] = None
    foto: Optional[Union[FotoBase64, str]] = None
    estado: Optional[str] = "pendiente"
    origen: Optional[str] = "vecino"
    fuente: Optional[str] = "formulario"
    latitud: Optional[float] = None
    longitud: Optional[float] = None


@app.get("/")
def home():
    return {"status": "ok", "app": "Provincia Libertaria API"}


def db_conn():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise HTTPException(status_code=500, detail="DATABASE_URL no configurada")
    return psycopg2.connect(database_url)


def normalizar_texto(valor: Optional[str]) -> Optional[str]:
    if valor is None:
        return None
    return " ".join(valor.strip().split()).title()


def normalizar_direccion(valor: Optional[str]) -> Optional[str]:
    if valor is None:
        return None
    limpio = " ".join(valor.strip().split())
    return limpio if limpio else None


def normalizar_numero(valor):
    if valor in (None, ""):
        return None
    try:
        return float(str(valor).replace(",", "."))
    except ValueError:
        return None


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
        "lomas-de-zamora": "Lomas De Zamora",
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


def limpiar_payload_webhook(payload: dict[str, Any]) -> dict[str, Any]:
    limpio = dict(payload)

    for campo in ("latitud", "longitud"):
        if limpio.get(campo) == "":
            limpio[campo] = None

    for campo in ("barrio", "categoria_detalle", "direccion", "foto"):
        if limpio.get(campo) == "":
            limpio[campo] = None

    return limpio


async def leer_payload_webhook(request: Request) -> tuple[dict[str, Any], Optional[UploadFile]]:
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        return limpiar_payload_webhook(await request.json()), None

    if (
        "application/x-www-form-urlencoded" in content_type
        or "multipart/form-data" in content_type
    ):
        form = await request.form()
        payload = {}
        foto_upload = None

        for key, value in form.multi_items():
            if hasattr(value, "filename") and hasattr(value, "file"):
                if key == "foto" and value.filename:
                    foto_upload = value
                else:
                    payload[key] = ""
                continue

            payload[key] = value

        return limpiar_payload_webhook(payload), foto_upload

    return limpiar_payload_webhook(await request.json()), None


def guardar_incidente_con_foto_json(
    incidente: IncidenteFotoJSON,
    foto_upload: Optional[UploadFile] = None
):
    if foto_upload:
        foto_url = procesar_foto_upload(foto_upload)
    else:
        foto_url = procesar_foto_webhook(incidente.foto)

    nuevo_id = insertar_incidente(
        ciudad=incidente.ciudad,
        barrio=incidente.barrio or "Sin especificar",
        categoria=incidente.categoria,
        descripcion=incidente.descripcion,
        categoria_detalle=incidente.categoria_detalle,
        direccion=incidente.direccion,
        foto_url=foto_url,
        estado=incidente.estado or "pendiente",
        origen=incidente.origen,
        fuente=incidente.fuente,
        latitud=incidente.latitud,
        longitud=incidente.longitud,
    )

    return {"ok": True, "id": nuevo_id, "foto_url": foto_url}


def url_publica_foto(foto_url: Optional[str]) -> Optional[str]:
    if not foto_url:
        return None

    parsed = urlparse(foto_url)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return foto_url

    return f"/foto/{foto_url.split('/')[-1]}"


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
            normalizar_texto(registro.ciudad),
            normalizar_texto(registro.barrio),
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
            categoria_detalle=incidente.categoria_detalle,
            direccion=incidente.direccion,
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


@app.post("/incidente-foto-json")
async def crear_incidente_con_foto_json(request: Request):
    try:
        payload, foto_upload = await leer_payload_webhook(request)
        incidente = IncidenteFotoJSON.model_validate(payload)
        return guardar_incidente_con_foto_json(incidente, foto_upload)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/incidentes/estado-lote")
def cambiar_estado_lote(
    ids: List[int] = Form(default=[]),
    estado: str = Form(...),
    volver: str = Form("/territorio/berisso"),
    admin = Depends(get_current_admin)
):
    if "/territorio/" in volver:
        distrito_slug = volver.split("/territorio/")[-1].split("?")[0].strip("/")
        requiere_distrito(distrito_slug, admin)

    actualizar_estado_incidentes(ids, estado)
    return RedirectResponse(url=volver, status_code=303)


@app.get("/incidentes/editar/{incidente_id}", response_class=HTMLResponse)
def editar_incidente_form(incidente_id: int, admin = Depends(get_current_admin)):
    conn = db_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, ciudad, barrio, categoria, categoria_detalle, descripcion, direccion,
               foto_url, estado, latitud, longitud, fecha_reporte
        FROM incidentes
        WHERE id = %s;
    """, (incidente_id,))

    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    (
        id_incidente,
        ciudad,
        barrio,
        categoria,
        categoria_detalle,
        descripcion,
        direccion,
        foto_url,
        estado,
        latitud,
        longitud,
        fecha_reporte,
    ) = row

    requiere_distrito(slug_desde_ciudad(ciudad), admin)

    fecha_value = fecha_reporte.strftime("%Y-%m-%dT%H:%M") if fecha_reporte else ""

    foto_html = ""
    if foto_url:
        foto_src = url_publica_foto(foto_url)
        foto_html = f"""
        <div class="foto-actual">
            <p><strong>Foto actual</strong></p>
            <img src="{html.escape(foto_src or '', quote=True)}" alt="Foto actual">
            <label class="checkline">
                <input type="checkbox" name="quitar_foto" value="1">
                Quitar foto actual
            </label>
        </div>
        """

    def selected(valor):
        return "selected" if (estado or "") == valor else ""

    html_response = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Editar reporte #{id_incidente}</title>
        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #48020c;
                color: #ffffff;
            }}

            .wrap {{
                max-width: 760px;
                margin: 0 auto;
                padding: 32px 18px;
            }}

            .box {{
                background: #650713;
                border: 1px solid #b98b31;
                border-radius: 16px;
                padding: 22px;
            }}

            h1 {{
                color: #f1d571;
                margin: 0 0 18px;
            }}

            label {{
                display: block;
                color: #f1d571;
                font-weight: 700;
                margin: 14px 0 6px;
            }}

            input, select, textarea {{
                width: 100%;
                padding: 12px 14px;
                border: 2px solid #b98b31;
                border-radius: 6px;
                background: #ffffff;
                color: #121212;
                box-sizing: border-box;
                font-size: 15px;
            }}

            textarea {{
                min-height: 150px;
            }}

            .row {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
            }}

            .actions {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
                margin-top: 20px;
            }}

            button, .volver {{
                border: 0;
                border-radius: 8px;
                padding: 12px 16px;
                font-weight: 700;
                cursor: pointer;
                text-decoration: none;
            }}

            button {{
                background: #f1d571;
                color: #121212;
            }}

            .volver {{
                background: #121212;
                color: #ffffff;
            }}

            .foto-actual {{
                margin-top: 16px;
                background: rgba(18,18,18,.35);
                border: 1px solid rgba(241,213,113,.45);
                border-radius: 12px;
                padding: 14px;
            }}

            .foto-actual img {{
                width: 100%;
                max-height: 260px;
                object-fit: cover;
                border-radius: 10px;
                display: block;
                margin-bottom: 10px;
            }}

            .checkline {{
                color: #ffffff;
                font-weight: 700;
            }}

            .checkline input {{
                width: auto;
                margin-right: 6px;
            }}

            @media (max-width: 720px) {{
                .row {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <main class="wrap">
            <div class="box">
                <h1>Editar reporte #{id_incidente}</h1>

                <form method="post" action="/incidentes/editar/{id_incidente}" enctype="multipart/form-data">
                    <div class="row">
                        <div>
                            <label>Ciudad</label>
                            <input name="ciudad" value="{html.escape(ciudad or '')}" required>
                        </div>
                        <div>
                            <label>Barrio / zona</label>
                            <input name="barrio" value="{html.escape(barrio or '')}" required>
                        </div>
                    </div>

                    <label>Dirección o referencia</label>
                    <input name="direccion" value="{html.escape(direccion or '')}">

                    <div class="row">
                        <div>
                            <label>Categoría</label>
                            <input name="categoria" value="{html.escape(categoria or '')}" required>
                        </div>
                        <div>
                            <label>Detalle de categoría</label>
                            <input name="categoria_detalle" value="{html.escape(categoria_detalle or '')}">
                        </div>
                    </div>

                    <label>Descripción</label>
                    <textarea name="descripcion" required>{html.escape(descripcion or '')}</textarea>

                    <div class="row">
                        <div>
                            <label>Estado</label>
                            <select name="estado">
                                <option value="pendiente" {selected('pendiente')}>pendiente</option>
                                <option value="publicado" {selected('publicado')}>publicado</option>
                                <option value="resuelto" {selected('resuelto')}>resuelto</option>
                                <option value="oculto" {selected('oculto')}>oculto</option>
                            </select>
                        </div>
                        <div>
                            <label>Fecha del reporte</label>
                            <input type="datetime-local" name="fecha_reporte" value="{html.escape(fecha_value)}">
                        </div>
                    </div>

                    <div class="row">
                        <div>
                            <label>Latitud</label>
                            <input name="latitud" value="{html.escape(str(latitud) if latitud is not None else '')}">
                        </div>
                        <div>
                            <label>Longitud</label>
                            <input name="longitud" value="{html.escape(str(longitud) if longitud is not None else '')}">
                        </div>
                    </div>

                    {foto_html}

                    <label>Subir nueva foto</label>
                    <input type="file" name="foto_nueva" accept="image/jpeg,image/png,image/webp">

                    <div class="actions">
                        <button type="submit">Guardar cambios</button>
                        <a class="volver" href="/territorio/{html.escape((ciudad or 'berisso').lower().replace(' ', '-'))}?estado=todos">Volver al panel</a>
                    </div>
                </form>
            </div>
        </main>
    </body>
    </html>
    """

    return HTMLResponse(content=html_response)
    
@app.get("/tablero", response_class=HTMLResponse)
def tablero():
    conn = db_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, ciudad, barrio, categoria, descripcion, latitud, longitud, fecha_reporte
        FROM incidentes
        WHERE latitud IS NOT NULL
          AND longitud IS NOT NULL
          AND estado = 'publicado'
        ORDER BY fecha_reporte DESC;
    """)

    puntos = cur.fetchall()

    cur.close()
    conn.close()

    puntos_js = []

    for item in puntos:
        id_incidente, ciudad, barrio, categoria, descripcion, latitud, longitud, fecha = item

        puntos_js.append({
            "id": id_incidente,
            "ciudad": ciudad or "",
            "barrio": barrio or "",
            "categoria": categoria or "",
            "descripcion": descripcion or "",
            "latitud": float(latitud),
            "longitud": float(longitud),
            "fecha": fecha.strftime("%d/%m/%Y %H:%M") if fecha else ""
        })

    puntos_json = json.dumps(puntos_js, ensure_ascii=False)

    html_response = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tablero Territorial - Provincia Libertaria</title>

        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">

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
                padding: 28px 18px;
            }}

            .eyebrow {{
                color: #f1d571;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: .08em;
                font-size: 13px;
            }}

            h1 {{
                margin: 8px 0 8px;
                font-size: 40px;
                color: #f1d571;
            }}

            .sub {{
                margin: 0 0 20px;
                color: #f7e7b0;
                font-size: 18px;
            }}

            #map {{
                height: 72vh;
                min-height: 480px;
                width: 100%;
                border-radius: 18px;
                border: 2px solid #b98b31;
                overflow: hidden;
                background: #121212;
            }}

            .panel {{
                background: #650713;
                border: 1px solid #b98b31;
                border-radius: 16px;
                padding: 18px;
                margin-bottom: 18px;
            }}

            .counter {{
                display: inline-block;
                color: #121212;
                background: #f1d571;
                padding: 8px 12px;
                border-radius: 999px;
                font-weight: 700;
                margin-top: 10px;
            }}

            .popup-title {{
                font-weight: 700;
                color: #9d1018;
                font-size: 16px;
                margin-bottom: 4px;
            }}

            .popup-meta {{
                font-size: 13px;
                color: #555;
                margin-bottom: 6px;
            }}

            .popup-desc {{
                font-size: 14px;
                color: #121212;
            }}
        </style>
    </head>
    <body>
        <main class="wrap">
            <section class="panel">
                <div class="eyebrow">Tablero territorial</div>
                <h1>Mapa de reportes</h1>
                <p class="sub">Primer tablero visual con reportes geolocalizados.</p>
                <span class="counter">{len(puntos_js)} reportes con ubicación</span>
            </section>

            <div id="map"></div>
        </main>

        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

        <script>
            const puntos = {puntos_json};

            const map = L.map('map').setView([-34.9, -57.9], 11);

            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
                maxZoom: 19,
                attribution: '&copy; OpenStreetMap'
            }}).addTo(map);

            const markers = [];

            puntos.forEach(function(p) {{
                const marker = L.marker([p.latitud, p.longitud]).addTo(map);

                marker.bindPopup(`
                    <div class="popup-title">${{p.categoria}}</div>
                    <div class="popup-meta">#${{p.id}} · ${{p.ciudad}} · ${{p.barrio}}</div>
                    <div class="popup-meta">${{p.fecha}}</div>
                    <div class="popup-desc">${{p.descripcion}}</div>
                `);

                markers.push(marker);
            }});

            if (markers.length > 0) {{
                const group = L.featureGroup(markers);
                map.fitBounds(group.getBounds().pad(0.2));
            }}
        </script>
    </body>
    </html>
    """

    return HTMLResponse(content=html_response)

@app.post("/incidentes/editar/{incidente_id}")
def editar_incidente_guardar(
    incidente_id: int,
    ciudad: str = Form(...),
    barrio: str = Form(...),
    direccion: str = Form(""),
    categoria: str = Form(...),
    categoria_detalle: str = Form(""),
    descripcion: str = Form(...),
    estado: str = Form("pendiente"),
    fecha_reporte: str = Form(""),
    latitud: str = Form(""),
    longitud: str = Form(""),
    quitar_foto: Optional[str] = Form(None),
    foto_nueva: Optional[UploadFile] = File(None),
    admin = Depends(get_current_admin),
):
    if estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=400, detail="Estado inválido")

    ciudad_norm = normalizar_texto(ciudad)
    barrio_norm = normalizar_texto(barrio)
    categoria_norm = normalizar_texto(categoria)
    categoria_detalle_norm = normalizar_direccion(categoria_detalle)
    direccion_norm = normalizar_direccion(direccion)
    latitud_val = normalizar_numero(latitud)
    longitud_val = normalizar_numero(longitud)
    fecha_val = fecha_reporte if fecha_reporte else None

    conn = db_conn()
    cur = conn.cursor()

    cur.execute("SELECT foto_url FROM incidentes WHERE id = %s;", (incidente_id,))
    row = cur.fetchone()

    if not row:
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    foto_url = row[0]

    cur.execute("SELECT ciudad FROM incidentes WHERE id = %s;", (incidente_id,))
    ciudad_original = cur.fetchone()[0]
    requiere_distrito(slug_desde_ciudad(ciudad_original), admin)
    requiere_distrito(slug_desde_ciudad(ciudad_norm), admin)

    if quitar_foto:
        foto_url = None

    if foto_nueva and foto_nueva.filename:
        foto_url = procesar_foto_upload(foto_nueva)

    cur.execute("""
        UPDATE incidentes
        SET ciudad = %s,
            barrio = %s,
            categoria = %s,
            categoria_detalle = %s,
            descripcion = %s,
            direccion = %s,
            foto_url = %s,
            estado = %s,
            latitud = %s,
            longitud = %s,
            fecha_reporte = COALESCE(%s::timestamp, fecha_reporte),
            fecha_actualizacion = NOW()
        WHERE id = %s;
    """, (
        ciudad_norm,
        barrio_norm,
        categoria_norm,
        categoria_detalle_norm,
        descripcion,
        direccion_norm,
        foto_url,
        estado,
        latitud_val,
        longitud_val,
        fecha_val,
        incidente_id,
    ))

    conn.commit()
    cur.close()
    conn.close()

    return RedirectResponse(
        url=f"/territorio/{ciudad_norm.lower().replace(' ', '-')}?estado=todos",
        status_code=303
    )




@app.get("/tercera-seccion", response_class=HTMLResponse)
def panel_tercera_seccion(admin = Depends(get_current_admin)):
    if admin.get("scope") not in ["todos", "tercera-seccion"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tenés permiso para ver la Tercera Sección"
        )

    conn = db_conn()
    cur = conn.cursor()

    distritos_data = []
    total_pendientes = 0
    total_publicados = 0
    total_resueltos = 0
    total_ocultos = 0

    for slug, ciudad in DISTRITOS_TERCERA:
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
            SELECT COUNT(*)
            FROM (
                SELECT INITCAP(LOWER(TRIM(barrio))) AS barrio_normalizado
                FROM incidentes
                WHERE LOWER(ciudad) = LOWER(%s)
                GROUP BY barrio_normalizado
            ) barrios;
        """, (ciudad,))
        barrios_activos = cur.fetchone()[0]

        cur.execute("""
            SELECT categoria, COUNT(*) AS total
            FROM incidentes
            WHERE LOWER(ciudad) = LOWER(%s)
            GROUP BY categoria
            ORDER BY total DESC
            LIMIT 4;
        """, (ciudad,))
        categorias_top = cur.fetchall()

        distritos_data.append({
            "slug": slug,
            "ciudad": ciudad,
            "pendientes": pendientes,
            "publicados": publicados,
            "resueltos": resueltos,
            "ocultos": ocultos,
            "barrios_activos": barrios_activos,
            "categorias_top": categorias_top,
        })

        total_pendientes += pendientes
        total_publicados += publicados
        total_resueltos += resueltos
        total_ocultos += ocultos

    cur.execute("""
        SELECT id, ciudad, barrio, categoria, descripcion, direccion, estado, fecha_reporte
        FROM incidentes
        WHERE LOWER(ciudad) IN ('berisso', 'ensenada', 'la plata')
        ORDER BY fecha_reporte DESC
        LIMIT 12;
    """)
    ultimos = cur.fetchall()

    cur.close()
    conn.close()

    cards_html = ""

    for d in distritos_data:
        categorias_html = ""

        if d["categorias_top"]:
            for categoria, total in d["categorias_top"]:
                categorias_html += f"<li><span>{html.escape(categoria or 'Sin categoría')}</span><strong>{total}</strong></li>"
        else:
            categorias_html = "<li><span>Sin datos</span><strong>0</strong></li>"

        cards_html += f"""
        <article class="district-card">
            <div class="district-head">
                <h2>{html.escape(d['ciudad'])}</h2>
                <span>{d['barrios_activos']} barrios activos</span>
            </div>

            <div class="mini-stats">
                <div><span>Pendientes</span><strong>{d['pendientes']}</strong></div>
                <div><span>Publicados</span><strong>{d['publicados']}</strong></div>
                <div><span>Resueltos</span><strong>{d['resueltos']}</strong></div>
                <div><span>Ocultos</span><strong>{d['ocultos']}</strong></div>
            </div>

            <div class="box-small">
                <h3>Categorías principales</h3>
                <ul>{categorias_html}</ul>
            </div>

            <div class="actions">
                <a href="/territorio/{html.escape(d['slug'])}">Administrar</a>
                <a href="/reportes/{html.escape(d['slug'])}">Ver público</a>
            </div>
        </article>
        """

    ultimos_html = ""

    if ultimos:
        for item in ultimos:
            id_incidente, ciudad, barrio, categoria, descripcion, direccion, estado_actual, fecha = item
            ciudad_safe = html.escape(ciudad or "")
            barrio_safe = html.escape(barrio or "")
            categoria_safe = html.escape(categoria or "")
            estado_safe = html.escape(estado_actual or "")
            fecha_safe = fecha.strftime('%d/%m/%Y %H:%M') if fecha else ""

            ultimos_html += f"""
            <li>
                <strong>#{id_incidente} · {ciudad_safe}</strong>
                <span>{categoria_safe} · {barrio_safe} · {estado_safe} · {fecha_safe}</span>
            </li>
            """
    else:
        ultimos_html = "<li><strong>Sin reportes</strong><span>Todavía no hay reportes cargados.</span></li>"

    html_response = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Tercera Sección - Provincia Libertaria</title>
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
                margin: 8px 0 8px;
                font-size: 42px;
                color: #f1d571;
            }}

            .sub {{
                margin: 0;
                color: #f7e7b0;
                font-size: 18px;
            }}

            .stats {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 14px;
                margin: 26px 0;
            }}

            .stat {{
                background: #650713;
                border: 1px solid #b98b31;
                border-radius: 12px;
                padding: 18px;
            }}

            .stat span {{
                display: block;
                color: #f1d571;
                font-size: 13px;
                margin-bottom: 8px;
            }}

            .stat strong {{
                font-size: 28px;
            }}

            .districts {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
                margin: 26px 0;
            }}

            .district-card {{
                background: #650713;
                border: 1px solid #b98b31;
                border-radius: 16px;
                padding: 18px;
            }}

            .district-head {{
                display: flex;
                justify-content: space-between;
                gap: 10px;
                align-items: start;
                margin-bottom: 14px;
            }}

            .district-head h2 {{
                margin: 0;
                color: #f1d571;
            }}

            .district-head span {{
                color: #f7e7b0;
                font-size: 13px;
                font-weight: 700;
            }}

            .mini-stats {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
                margin-bottom: 14px;
            }}

            .mini-stats div {{
                background: rgba(18,18,18,.32);
                border-radius: 10px;
                padding: 10px;
            }}

            .mini-stats span {{
                display: block;
                color: #f1d571;
                font-size: 12px;
            }}

            .mini-stats strong {{
                font-size: 22px;
            }}

            .box-small {{
                background: rgba(18,18,18,.28);
                border-radius: 12px;
                padding: 12px;
                margin-bottom: 14px;
            }}

            .box-small h3 {{
                margin: 0 0 8px;
                color: #f1d571;
                font-size: 16px;
            }}

            ul {{
                list-style: none;
                padding: 0;
                margin: 0;
            }}

            .box-small li {{
                display: flex;
                justify-content: space-between;
                padding: 7px 0;
                border-bottom: 1px solid rgba(241,213,113,.18);
            }}

            .box-small li:last-child {{
                border-bottom: 0;
            }}

            .actions {{
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }}

            .actions a {{
                display: inline-block;
                background: #f1d571;
                color: #121212;
                padding: 10px 12px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 700;
            }}

            .actions a:last-child {{
                background: #121212;
                color: #ffffff;
                border: 1px solid #b98b31;
            }}

            .latest {{
                background: #650713;
                border: 1px solid #b98b31;
                border-radius: 16px;
                padding: 18px;
                margin-top: 22px;
            }}

            .latest h2 {{
                color: #f1d571;
                margin-top: 0;
            }}

            .latest li {{
                display: grid;
                gap: 4px;
                padding: 11px 0;
                border-bottom: 1px solid rgba(241,213,113,.2);
            }}

            .latest li:last-child {{
                border-bottom: 0;
            }}

            .latest span {{
                color: #f7e7b0;
            }}

            @media (max-width: 900px) {{
                .stats {{
                    grid-template-columns: repeat(2, 1fr);
                }}

                .districts {{
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
                <div class="eyebrow">Panel general</div>
                <h1>Tercera Sección</h1>
                <p class="sub">Resumen territorial de Berisso, Ensenada y La Plata.</p>
            </section>

            <section class="stats">
                <div class="stat"><span>Pendientes</span><strong>{total_pendientes}</strong></div>
                <div class="stat"><span>Publicados</span><strong>{total_publicados}</strong></div>
                <div class="stat"><span>Resueltos</span><strong>{total_resueltos}</strong></div>
                <div class="stat"><span>Ocultos</span><strong>{total_ocultos}</strong></div>
            </section>

            <section class="districts">
                {cards_html}
            </section>

            <section class="latest">
                <h2>Últimos reportes de la sección</h2>
                <ul>
                    {ultimos_html}
                </ul>
            </section>
        </main>
    </body>
    </html>
    """

    return HTMLResponse(content=html_response)


@app.get("/panel/berisso")
def redirigir_panel_berisso():
    return RedirectResponse(url="/territorio/berisso", status_code=301)


@app.get("/panel/ensenada")
def redirigir_panel_ensenada():
    return RedirectResponse(url="/territorio/ensenada", status_code=301)


@app.get("/panel/la-plata")
def redirigir_panel_la_plata():
    return RedirectResponse(url="/territorio/la-plata", status_code=301)


@app.get("/territorio/{distrito_slug}", response_class=HTMLResponse)
def panel_distrito(distrito_slug: str, estado: str = "pendiente", admin = Depends(get_current_admin)):
    requiere_distrito(distrito_slug, admin)

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
        SELECT INITCAP(LOWER(TRIM(barrio))) AS barrio_normalizado, COUNT(*) AS total
        FROM incidentes
        WHERE LOWER(ciudad) = LOWER(%s)
        GROUP BY barrio_normalizado
        ORDER BY total DESC;
    """, (ciudad,))
    barrios = cur.fetchall()

    barrios_activos = len(barrios)

    if estado == "todos":
        cur.execute("""
            SELECT id, barrio, categoria, categoria_detalle, descripcion, direccion, foto_url, fecha_reporte, estado
            FROM incidentes
            WHERE LOWER(ciudad) = LOWER(%s)
            ORDER BY fecha_reporte DESC
            LIMIT 24;
        """, (ciudad,))
    else:
        cur.execute("""
            SELECT id, barrio, categoria, categoria_detalle, descripcion, direccion, foto_url, fecha_reporte, estado
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
        id_incidente, barrio, categoria, categoria_detalle, descripcion, direccion, foto_url, fecha, estado_actual = item

        barrio_safe = html.escape(barrio or "")
        categoria_safe = html.escape(categoria or "")
        categoria_detalle_safe = html.escape(categoria_detalle or "")
        descripcion_safe = html.escape(descripcion or "")
        direccion_safe = html.escape(direccion or "")
        estado_safe = html.escape(estado_actual or "")

        categoria_detalle_html = f'<p class="direccion">🏷️ {categoria_detalle_safe}</p>' if categoria_detalle_safe else ""
        direccion_html = f'<p class="direccion">🧭 {direccion_safe}</p>' if direccion_safe else ""

        if foto_url:
            foto_src = url_publica_foto(foto_url)
            imagen_html = f'<img src="{html.escape(foto_src or "", quote=True)}" alt="Foto del reporte">'
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
                {categoria_detalle_html}
                <p class="barrio">📍 {barrio_safe}</p>
                {direccion_html}
                <p>{descripcion_safe}</p>
                <p><a class="edit-link" href="/incidentes/editar/{id_incidente}">Editar</a></p>
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
            <span>{html.escape(barrio or "Sin Barrio")}</span>
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

            .btn-resuelto {{
                background: #24a148;
                color: #ffffff;
            }}

            .btn-publicar {{
                background: #f1d571;
                color: #121212;
            }}

            .btn-pendiente {{
                background: #9d1018;
                color: #ffffff;
            }}

            .btn-oculto {{
                background: #121212;
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
                background: #24a148;
                color: #ffffff;
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
                margin: 0 0 8px;
                font-weight: 700;
            }}

            .direccion {{
                margin: 0 0 10px;
                font-weight: 700;
                color: #555;
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
                    <button class="btn-resuelto" type="submit" name="estado" value="resuelto">Marcar resuelto</button>
                    <button class="btn-publicar" type="submit" name="estado" value="publicado">Aprobar / Publicar</button>
                    <button class="btn-pendiente" type="submit" name="estado" value="pendiente">Volver a pendiente</button>
                    <button class="btn-oculto" type="submit" name="estado" value="oculto">Ocultar</button>
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
        SELECT COUNT(*)
        FROM incidentes
        WHERE LOWER(ciudad) = LOWER(%s)
          AND estado = 'publicado';
    """, (ciudad,))
    reportes_publicados = cur.fetchone()[0]

    cur.execute("""
        SELECT INITCAP(LOWER(TRIM(barrio))) AS barrio_normalizado, COUNT(*) AS total
        FROM incidentes
        WHERE LOWER(ciudad) = LOWER(%s)
          AND estado = 'publicado'
        GROUP BY barrio_normalizado
        ORDER BY total DESC;
    """, (ciudad,))
    barrios = cur.fetchall()

    cur.execute("""
        SELECT categoria, COUNT(*) AS total
        FROM incidentes
        WHERE LOWER(ciudad) = LOWER(%s)
          AND estado = 'publicado'
        GROUP BY categoria
        ORDER BY total DESC;
    """, (ciudad,))
    categorias = cur.fetchall()

    cur.execute("""
        SELECT id, barrio, categoria, categoria_detalle, descripcion, direccion, foto_url, fecha_reporte
        FROM incidentes
        WHERE LOWER(ciudad) = LOWER(%s)
          AND estado = 'publicado'
        ORDER BY fecha_reporte DESC
        LIMIT 24;
    """, (ciudad,))
    incidentes = cur.fetchall()

    cur.close()
    conn.close()

    barrios_activos = len(barrios)
    categorias_detectadas = len(categorias)

    cards_html = ""

    for item in incidentes:
        id_incidente, barrio, categoria, categoria_detalle, descripcion, direccion, foto_url, fecha = item

        barrio_safe = html.escape(barrio or "")
        categoria_safe = html.escape(categoria or "")
        categoria_detalle_safe = html.escape(categoria_detalle or "")
        descripcion_safe = html.escape(descripcion or "")
        direccion_safe = html.escape(direccion or "")

        categoria_detalle_html = f'<p class="direccion">🏷️ {categoria_detalle_safe}</p>' if categoria_detalle_safe else ""
        direccion_html = f'<p class="direccion">🧭 {direccion_safe}</p>' if direccion_safe else ""

        if foto_url:
            foto_src = url_publica_foto(foto_url)
            imagen_html = f'<img src="{html.escape(foto_src or "", quote=True)}" alt="Foto del reporte">'
        else:
            imagen_html = '<div class="sin-foto">Sin foto</div>'

        cards_html += f"""
        <article class="card">
            <div class="thumb">{imagen_html}</div>
            <div class="contenido">
                <div class="meta">#{id_incidente} · {fecha.strftime('%d/%m/%Y %H:%M')}</div>
                <h3>{categoria_safe}</h3>
                {categoria_detalle_html}
                <p class="barrio">📍 {barrio_safe}</p>
                {direccion_html}
                <p>{descripcion_safe}</p>
            </div>
        </article>
        """

    barrios_html = ""

    for barrio, total in barrios:
        barrios_html += f"""
        <li>
            <span>{html.escape(barrio or "Sin Barrio")}</span>
            <strong>{total}</strong>
        </li>
        """

    categorias_html = ""

    for categoria, total in categorias:
        categorias_html += f"""
        <li>
            <span>{html.escape(categoria)}</span>
            <strong>{total}</strong>
        </li>
        """

    if not cards_html:
        cards_html = '<p class="vacio">Todavía no hay reportes publicados para este distrito.</p>'

    if not barrios_html:
        barrios_html = '<li><span>Sin barrios activos</span><strong>0</strong></li>'

    if not categorias_html:
        categorias_html = '<li><span>Sin categorías</span><strong>0</strong></li>'

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
                margin: 8px 0 8px;
                font-size: 42px;
                color: #f1d571;
            }}

            .sub {{
                margin: 0;
                color: #f7e7b0;
                font-size: 18px;
            }}

            .hero {{
                background: linear-gradient(135deg, #650713, #48020c);
                border: 1px solid #b98b31;
                border-radius: 18px;
                padding: 28px;
                margin-bottom: 24px;
            }}

            .claim {{
                margin-top: 22px;
                background: rgba(18,18,18,.35);
                border-left: 4px solid #f1d571;
                padding: 16px 18px;
                border-radius: 12px;
            }}

            .claim h2 {{
                margin: 0 0 8px;
                color: #ffffff;
                font-size: 24px;
            }}

            .claim p {{
                margin: 0;
                color: #f1d571;
                font-size: 18px;
                font-weight: 700;
            }}

            .stats {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 14px;
                margin: 24px 0;
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
            }}

            .thumb {{
                width: 100%;
                height: 210px;
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
                margin: 0 0 8px;
                font-weight: 700;
            }}

            .direccion {{
                margin: 0 0 10px;
                font-weight: 700;
                color: #555;
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

            .cta {{
                margin-top: 24px;
                background: #650713;
                border: 1px solid #b98b31;
                border-radius: 14px;
                padding: 20px;
                text-align: center;
            }}

            .cta a {{
                display: inline-block;
                margin-top: 10px;
                color: #121212;
                background: #f1d571;
                padding: 12px 18px;
                border-radius: 8px;
                font-weight: 700;
                text-decoration: none;
            }}

            .vacio {{
                color: #f1d571;
                font-weight: 700;
            }}

            @media (max-width: 850px) {{
                .stats {{
                    grid-template-columns: 1fr;
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
            <section class="hero">
                <div class="eyebrow">Mapa de Barrio</div>
                <h1>Reportes de {html.escape(ciudad)}</h1>
                <p class="sub">Problemas reales informados por vecinos y publicados por referentes territoriales.</p>

                <div class="claim">
                    <h2>Escucha activa las 24 horas</h2>
                    <p>La política del siglo XXI no toca timbres. Escucha, mide y resuelve.</p>
                </div>
            </section>

            <section class="stats">
                <div class="stat">
                    <span>Reportes publicados</span>
                    <strong>{reportes_publicados}</strong>
                </div>
                <div class="stat">
                    <span>Barrios activos</span>
                    <strong>{barrios_activos}</strong>
                </div>
                <div class="stat">
                    <span>Categorías detectadas</span>
                    <strong>{categorias_detectadas}</strong>
                </div>
            </section>

            <section class="grid">
                <div>
                    <h2>Últimos reportes publicados</h2>
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

            <section class="cta">
                <strong>¿Detectaste un problema en tu barrio?</strong>
                <br>
                <a href="https://provincialibertaria.com/reporta-tu-barrio/">Informar incidente</a>
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
