from typing import Optional


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
        "la-matanza": "La Matanza",
    }

    return mapa.get(slug.lower(), slug.replace("-", " ").title())
