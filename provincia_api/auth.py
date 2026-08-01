import os
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from provincia_api.config import DISTRITOS_TERCERA


security = HTTPBasic()


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
            "scope": scope.strip(),
        }

    return users


def get_current_admin(credentials: HTTPBasicCredentials = Depends(security)):
    users = parse_admin_users()

    if not users:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ADMIN_USERS no configurado",
        )

    user_data = users.get(credentials.username)

    valid_user = user_data is not None
    valid_password = (
        valid_user
        and secrets.compare_digest(credentials.password, user_data["password"])
    )

    if not valid_user or not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña inválidos",
            headers={"WWW-Authenticate": "Basic"},
        )

    return {
        "username": credentials.username,
        "scope": user_data["scope"],
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
            detail="No tenés permiso para ver este distrito",
        )
