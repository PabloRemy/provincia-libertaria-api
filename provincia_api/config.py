import os


DATA_DIR = os.getenv("DATA_DIR", "/data")
UPLOAD_ROOT = os.path.join(DATA_DIR, "uploads")
UPLOAD_DIR = os.path.join(UPLOAD_ROOT, "incidentes")
PUBLIC_UPLOAD_BASE = "/uploads/incidentes"

ESTADOS_VALIDOS = ["pendiente", "publicado", "resuelto", "oculto"]

DISTRITOS_TERCERA = [
    ("berisso", "Berisso"),
    ("ensenada", "Ensenada"),
    ("la-plata", "La Plata"),
]
