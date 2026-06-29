from unittest.mock import patch

import pytest
from fastapi import HTTPException

from main import IncidenteFotoJSON, crear_incidente_con_foto_json, url_publica_foto


def payload_cf7(**changes):
    payload = {
        "ciudad": "Berisso",
        "categoria": "Iluminación",
        "descripcion": "Luminaria apagada",
        "direccion": "Calle 12 345",
        "latitud": "-34.87",
        "longitud": "-57.88",
    }
    payload.update(changes)
    return payload


@patch("main.insertar_incidente", return_value=101)
def test_webhook_acepta_envio_sin_barrio_ni_foto(insertar):
    incidente = IncidenteFotoJSON.model_validate(payload_cf7())
    response = crear_incidente_con_foto_json(incidente)

    assert response == {"ok": True, "id": 101, "foto_url": None}
    assert insertar.call_args.kwargs["barrio"] == "Sin especificar"
    assert insertar.call_args.kwargs["foto_url"] is None


@patch("main.insertar_incidente", return_value=102)
def test_webhook_acepta_foto_vacia_enviada_por_cf7(insertar):
    incidente = IncidenteFotoJSON.model_validate(payload_cf7(foto=""))
    response = crear_incidente_con_foto_json(incidente)

    assert response["foto_url"] is None
    assert insertar.call_args.kwargs["foto_url"] is None


@patch("main.insertar_incidente", return_value=103)
def test_webhook_acepta_enlace_de_foto_enviado_por_plugin(insertar):
    foto = "https://provincialibertaria.com/wp-content/uploads/reporte.jpg"
    incidente = IncidenteFotoJSON.model_validate(
        payload_cf7(barrio="Centro", foto=foto)
    )
    response = crear_incidente_con_foto_json(incidente)

    assert response["foto_url"] == foto
    assert insertar.call_args.kwargs["foto_url"] == foto


def test_webhook_rechaza_ruta_de_foto_que_no_es_url():
    incidente = IncidenteFotoJSON.model_validate(
        payload_cf7(foto="/tmp/archivo.jpg")
    )

    with pytest.raises(HTTPException) as error:
        crear_incidente_con_foto_json(incidente)

    assert error.value.status_code == 400
    assert error.value.detail == "URL de foto inválida"


def test_url_publica_foto_conserva_enlaces_y_resuelve_archivos_locales():
    externa = "https://provincialibertaria.com/uploads/reporte.jpg"

    assert url_publica_foto(externa) == externa
    assert url_publica_foto("/uploads/incidentes/local.webp") == "/foto/local.webp"
