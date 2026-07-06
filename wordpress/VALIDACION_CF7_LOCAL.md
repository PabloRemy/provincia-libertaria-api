# Validación local de CF7

Usar esta guía cuando los contenedores estén `healthy` pero Codex no pueda
acceder a `127.0.0.1` por aislamiento del entorno.

## 1. Verificar servicios

```bash
cd /home/lab/Documentos/provincialibertaria/provincia-libertaria-api
sudo docker compose -f compose.test.yml ps
curl -sS http://127.0.0.1:8000/
curl -sS -I http://127.0.0.1:8080/
```

## 2. Probar el webhook directo

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

Resultado esperado:

```json
{"ok":true,"id":1,"foto_url":null}
```

El `id` puede ser otro número si ya existen reportes cargados.

## 3. Verificar que se guardó en PostgreSQL

```bash
sudo docker compose -f compose.test.yml exec -T postgres-test \
  psql -U provincia_test -d provincia_libertaria_test \
  -c "SELECT id, ciudad, barrio, categoria, descripcion, foto_url, estado FROM incidentes ORDER BY id DESC LIMIT 5;"
```

El reporte sin barrio debe aparecer con `barrio = Sin especificar`.

## 4. Verificar CF7 en WordPress

Abrir:

```text
http://127.0.0.1:8080/wp-admin
```

En el formulario `Reporte de barrio local` verificar:

- Formulario: usar `wordpress/cf7-formulario-reporte.txt`.
- Webhook: `http://api-test.local:8000/incidente-foto-json`.
- Ajustes adicionales: `skip_mail: on`.

Crear una página local con el shortcode del formulario, abrirla y enviar un
reporte sin barrio, sin foto y sin GPS.

## 5. Confirmar el envío desde WordPress

Volver a consultar PostgreSQL:

```bash
sudo docker compose -f compose.test.yml exec -T postgres-test \
  psql -U provincia_test -d provincia_libertaria_test \
  -c "SELECT id, ciudad, barrio, categoria, descripcion, foto_url, estado, fuente FROM incidentes ORDER BY id DESC LIMIT 5;"
```

La última fila debe corresponder al reporte enviado desde la página local.
