# Validación local de Contact Form 7

Procedimiento y resultados validados el 13/14 de julio de 2026. Todo el escenario
usa datos ficticios, servicios Docker locales y la base
`provincia_libertaria_test`. No contiene credenciales reales y no se conectó a
producción.

## 1. Verificar servicios

```bash
cd /home/desk/Documentos/Proyectos/provincia-libertaria-api
sudo docker compose -f compose.test.yml up -d --wait
sudo docker compose -f compose.test.yml ps
curl -sS http://127.0.0.1:8000/
curl -sS -I http://127.0.0.1:8000/docs
curl -sS -I http://127.0.0.1:8000/openapi.json
curl -sS -I http://127.0.0.1:8080/
```

Resultado validado: `postgres-test`, `api-test`, `mysql-wordpress-test` y
`wordpress-test` en estado `healthy`; FastAPI, documentación, OpenAPI y
WordPress accesibles. PostgreSQL se publica sólo en `127.0.0.1:55432`.

## 2. Cargar y verificar datos ficticios

```bash
sudo docker compose -f compose.test.yml --profile tools run --rm seed-test
sudo docker compose -f compose.test.yml exec -T postgres-test \
  psql -U provincia_test -d provincia_libertaria_test \
  -c "SELECT count(*) FROM incidentes; SELECT count(*) FROM reclutamiento_registros;"
```

Resultado validado: 9 incidentes y 3 registros de reclutamiento ficticios. Las
tablas `incidentes` y `reclutamiento_registros` existen en la base local `_test`.

## 3. Probar el webhook directo

```bash
curl -sS -X POST http://127.0.0.1:8000/incidente-foto-json \
  -H 'Content-Type: application/json' \
  -d '{
    "ciudad": "Berisso",
    "categoria": "Iluminación",
    "descripcion": "Prueba local desde curl",
    "direccion": "Calle local 123",
    "latitud": null,
    "longitud": null
  }'
```

El resultado esperado contiene `"ok": true`, un `id` nuevo y `foto_url: null`.
El identificador depende del estado local de la base.

## 4. Configurar WordPress y CF7 local

- WordPress: `http://127.0.0.1:8080`.
- Contact Form 7 instalado y activado.
- Formulario: `Reporte de barrio local`.
- Contenido: `wordpress/cf7-formulario-reporte.txt`.
- Shortcode: `[contact-form-7 id="44e0661" title="Reporte de barrio local"]`.
- Ajuste adicional: `skip_mail: on`.
- Mu-plugin: `wordpress/mu-plugins/provincia-libertaria-cf7-local.php`.
- Webhook interno: `http://api-test.local:8000/incidente-foto-json`.

El mu-plugin gestiona el webhook. No se instaló un plugin externo de webhooks y
el entorno no envía correos.

## 5. Validación CF7 sin foto

Se envió el formulario sin adjuntar archivo y se verificó en PostgreSQL:

- Incidente: `id=10`.
- Descripción: `Prueba local desde Contact Form 7 sin foto`.
- Ciudad: Berisso.
- Barrio: Centro.
- Categoría: Iluminación.
- Estado: `pendiente`.
- Fuente: `formulario`.
- `foto_url`: vacío, comportamiento correcto sin archivo adjunto.

Consulta reproducible:

```bash
sudo docker compose -f compose.test.yml exec -T postgres-test \
  psql -U provincia_test -d provincia_libertaria_test \
  -c "SELECT id, ciudad, barrio, categoria, descripcion, foto_url, estado, fuente FROM incidentes ORDER BY id DESC LIMIT 5;"
```

## 6. Validación CF7 con foto

Se envió una imagen JPG mediante el mismo formulario y se verificó:

- Incidente: `id=11`.
- Descripción: `Prueba local desde Contact Form 7 con foto`.
- Ciudad: Berisso.
- Barrio: Los Talas.
- Categoría: Iluminación.
- Estado: `pendiente`.
- Fuente: `formulario`.
- `foto_url`: `/uploads/incidentes/c18aeb7d237d49618da72dc926c17e8b.webp`.
- Log de WordPress: `Provincia Libertaria CF7 local foto legible`.
- JPG recibido: 18161 bytes.
- WebP creado en
  `/data/uploads/incidentes/c18aeb7d237d49618da72dc926c17e8b.webp`.
- Tamaño WebP: 5702 bytes.

La ruta `/foto/c18aeb7d237d49618da72dc926c17e8b.webp` mostró visualmente la
imagen. La ruta `/uploads/...` provocó la descarga del archivo; se registra como
comportamiento observado, no como falla. El panel de Berisso mostró el reporte y
la foto correctamente.

## 7. Verificación visual

Se validaron visualmente:

- Panel de Tercera Sección.
- Paneles de Berisso, Ensenada y La Plata.
- Tablero territorial y marcadores ficticios.
- Autenticación administrativa local.
- Reporte con foto en el panel de Berisso.
- Imagen servida por `/foto/{nombre}`.

## 8. Persistencia

Se ejecutó el apagado sin eliminar volúmenes y luego se levantó nuevamente:

```bash
sudo docker compose -f compose.test.yml down
sudo docker compose -f compose.test.yml up -d --wait
```

Después del reinicio:

- WordPress conservó usuario, página y formulario.
- PostgreSQL conservó el incidente `id=11`.
- El archivo WebP persistió.
- El panel siguió mostrando el reporte y la foto.
- Git continuó limpio.

No usar `down -v` si se desea conservar el escenario. Esta validación confirma
el flujo local actual; no confirma el código ni la configuración desplegados en
producción.
