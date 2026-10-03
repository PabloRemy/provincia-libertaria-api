from typing import Optional, Union

from pydantic import BaseModel


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
