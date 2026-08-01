# Continuar desde aquí

Actualizado: 2026-08-01.

## Punto de partida verificado

- Repositorio: `https://github.com/PabloRemy/provincia-libertaria-api.git`.
- Clon local: `/home/desk/Documentos/Proyectos/provincia-libertaria-api`.
- Rama activa de desarrollo: `integracion-local-sobre-github`.
- Commit de partida de la validación local: `2a8b556`.
- La rama local coincidía con `origin/integracion-local-sobre-github` y el árbol
  estaba limpio antes y después de las validaciones.
- Rama productiva: `main`; `origin/main` permanece en `abc9807`.
- El contrato OpenAPI público de producción coincide exactamente con
  `origin/main` (`abc9807`). Esto identifica la línea productiva con evidencia
  fuerte, aunque el hash interno del contenedor todavía requiere consulta de
  solo lectura en Coolify o el VPS.

## Decisión de sincronización

`main` e `integracion-local-sobre-github` tienen historiales independientes y
no poseen ancestro común. No ejecutar `pull`, merge ni rebase automático entre
ellas. `main` conserva la referencia productiva e histórica;
`integracion-local-sobre-github` es la fuente de verdad técnica para desarrollo.

La sincronización futura debe ser manual, revisada y controlada.

## Estado de trabajo confirmado

- Linux Mint 22.3 Zena sobre Ubuntu Noble `amd64`, Python 3.12.3 y `.venv`
  operativos. Docker Engine y Docker Compose instalados y comprobados.
- Suite sin PostgreSQL: 30 aprobadas, 1 deseleccionada y 1 advertencia. Suite
  completa con `TEST_DATABASE_URL`: 31 aprobadas y 1 advertencia.
- La `StarletteDeprecationWarning` por Starlette/httpx es una mejora técnica no
  bloqueante.
- `postgres-test`, `api-test`, `mysql-wordpress-test` y `wordpress-test`
  alcanzaron estado `healthy`.
- FastAPI, `/docs`, `/openapi.json`, WordPress, paneles territoriales, tablero,
  marcadores ficticios y autenticación administrativa fueron validados.
- La base aislada `provincia_libertaria_test` recibió 9 incidentes y 3 registros
  ficticios de reclutamiento.
- WordPress y CF7 fueron validados con y sin foto mediante el mu-plugin local,
  sin plugin externo de webhooks ni envío de correo.
- La carga CF7 con foto funciona extremo a extremo en local: el incidente 11,
  `foto_url`, archivo WebP, ruta `/foto/...` y panel de Berisso fueron
  verificados visualmente.
- La persistencia de WordPress, PostgreSQL y el WebP se conservó después de
  `docker compose down` sin `-v` y un nuevo arranque.
- Producción permaneció intacta. No se comparó todavía la rama de integración
  con el código y la configuración efectivamente desplegados.

## Próximo paso exacto

El endpoint temporal `/debug` fue retirado de la rama local de desarrollo y se
agregó una prueba que exige una respuesta `404`. La suite sin PostgreSQL quedó
en 31 pruebas aprobadas, 1 omitida y 1 advertencia no bloqueante.

La comparación de Dockerfiles y la auditoría pública de producción están
registradas en `AUDITORIA_PRODUCCION_LECTURA_2026-08-01.md`.

1. Obtener o documentar acceso de solo lectura a Coolify/VPS.
2. Confirmar imagen, commit y configuración del contenedor sin revelar secretos.
3. Comparar esquema y persistencia con el entorno local sin modificar datos.
4. Preparar un procedimiento de publicación con respaldo, comprobaciones
   posteriores y reversión.

No modificar producción, no integrar historiales y no desplegar sin autorización
expresa.
