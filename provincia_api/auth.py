import base64
import binascii
import hashlib
import hmac
import json
import os
import re
import secrets
import sqlite3
import time
from contextlib import contextmanager

from fastapi import HTTPException, Request, status

from provincia_api.config import DISTRITOS_TERCERA


SESSION_COOKIE = "pl_admin_session"
SESSION_AGE = 8 * 60 * 60


class AdminLoginRequired(Exception):
    pass


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


def session_secret() -> bytes:
    secret = os.getenv("SESSION_SECRET_KEY", "")
    if len(secret) < 32:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Sesión administrativa no configurada",
        )
    return secret.encode("utf-8")


def secure_session_cookie() -> bool:
    return os.getenv("SESSION_COOKIE_SECURE", "true").lower() != "false"


def authenticate_admin(username: str, password: str):
    users = parse_admin_users()
    if not users:
        raise HTTPException(status_code=500, detail="ADMIN_USERS no configurado")
    user_data = users.get(username)
    expected = user_data["password"] if user_data else ""
    if not secrets.compare_digest(password, expected) or not user_data:
        return None
    return {"username": username, "scope": user_data["scope"]}


def destination_for_scope(scope: str) -> str:
    if scope in ("todos", "tercera-seccion"):
        return "/tercera-seccion"
    if re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", scope):
        return f"/territorio/{scope}"
    raise HTTPException(status_code=500, detail="Scope administrativo inválido")


def create_session(admin: dict) -> str:
    secret = session_secret()
    password = parse_admin_users()[admin["username"]]["password"]
    payload = json.dumps(
        {
            "username": admin["username"],
            "expires": int(time.time()) + SESSION_AGE,
            "nonce": secrets.token_urlsafe(24),
        },
        separators=(",", ":"),
    ).encode("utf-8")
    body = base64.urlsafe_b64encode(payload).rstrip(b"=").decode("ascii")
    signature = hmac.new(
        secret + password.encode("utf-8"), body.encode("ascii"), hashlib.sha256
    ).hexdigest()
    token = f"{body}.{signature}"
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    try:
        with session_db() as conn:
            conn.execute(
                "INSERT INTO active_sessions (token_hash, expires) VALUES (?, ?)",
                (token_hash, int(time.time()) + SESSION_AGE),
            )
            conn.execute("DELETE FROM active_sessions WHERE expires < ?", (int(time.time()),))
    except sqlite3.Error:
        raise HTTPException(status_code=503, detail="Almacén de sesiones no disponible") from None
    return token


def get_current_admin(request: Request):
    secret = session_secret()
    users = parse_admin_users()
    if not users:
        raise HTTPException(status_code=500, detail="ADMIN_USERS no configurado")
    token = request.cookies.get(SESSION_COOKIE, "")
    try:
        body, signature = token.split(".", 1)
        payload = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
        username = payload["username"]
        expires = payload["expires"]
        user_data = users.get(username)
        if not user_data or not isinstance(expires, int) or expires <= time.time():
            raise ValueError
        expected = hmac.new(
            secret + user_data["password"].encode("utf-8"),
            body.encode("ascii"),
            hashlib.sha256,
        ).hexdigest()
        if not secrets.compare_digest(signature, expected):
            raise ValueError
    except (ValueError, KeyError, TypeError, UnicodeError, binascii.Error):
        raise AdminLoginRequired from None
    if not session_is_active(token):
        raise AdminLoginRequired
    return {"username": username, "scope": user_data["scope"]}


@contextmanager
def session_db():
    data_dir = os.getenv("DATA_DIR", "/data")
    conn = None
    try:
        os.makedirs(data_dir, exist_ok=True)
        conn = sqlite3.connect(os.path.join(data_dir, "admin_sessions.sqlite3"))
        conn.execute(
            "CREATE TABLE IF NOT EXISTS active_sessions "
            "(token_hash TEXT PRIMARY KEY, expires INTEGER NOT NULL)"
        )
    except (OSError, sqlite3.Error):
        if conn is not None:
            conn.close()
        raise HTTPException(status_code=503, detail="Almacén de sesiones no disponible") from None
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def session_is_active(token: str) -> bool:
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    try:
        with session_db() as conn:
            return conn.execute(
                "SELECT 1 FROM active_sessions WHERE token_hash = ? AND expires > ?",
                (token_hash, int(time.time())),
            ).fetchone() is not None
    except sqlite3.Error:
        raise HTTPException(status_code=503, detail="Almacén de sesiones no disponible") from None


def revoke_session(token: str):
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    try:
        with session_db() as conn:
            conn.execute(
                "DELETE FROM active_sessions WHERE token_hash = ?", (token_hash,)
            )
    except sqlite3.Error:
        raise HTTPException(status_code=503, detail="Almacén de sesiones no disponible") from None


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
