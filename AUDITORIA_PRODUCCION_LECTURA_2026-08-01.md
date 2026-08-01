# Auditoría de producción en modo lectura — 2026-08-01

## Alcance y seguridad

Esta auditoría se realizó exclusivamente mediante consultas públicas y comandos
Git locales de lectura. No se enviaron formularios, no se ejecutaron solicitudes
POST, no se accedió a bases de datos, no se modificaron archivos del VPS y no se
reiniciaron ni desplegaron servicios.

## Superficie pública observada

- Sitio WordPress: `https://provincialibertaria.com`.
- API y tablero: `https://mapa.provincialibertaria.com`.
- La raíz de la API respondió `200` con:
  `{"status":"ok","app":"Provincia Libertaria API"}`.
- La API pública responde mediante Uvicorn.
- `/docs` y `/openapi.json` están expuestos públicamente.
- El certificado TLS de `mapa.provincialibertaria.com` estaba vigente al momento
  de la consulta.

## Identificación de la versión productiva

Se obtuvo el contrato público desde:

`https://mapa.provincialibertaria.com/openapi.json`

Luego se generó localmente el contrato OpenAPI para las referencias Git conocidas
y se compararon representaciones JSON canónicas.

| Referencia | Resultado frente a producción |
|---|---|
| `origin/main` (`abc9807`) | Coincidencia OpenAPI exacta |
| `origin/integracion-local-sobre-github` (`d359d9d`) | Mismas rutas, esquemas diferentes |
| rama local (`b491bc5`) | Diferente; local ya no expone `/debug` |

Huella SHA-256 del OpenAPI público canónico:

`63023b8e3bf828273dc1018190bdd2d0005c26cc002392bbca95568e0e708939`

La coincidencia exacta demuestra que el **contrato API actualmente publicado**
corresponde a `origin/main`. Es evidencia fuerte de que producción usa esa línea
de código, pero no prueba por sí sola el hash interno de la imagen o contenedor:
otro artefacto con el mismo contrato podría producir la misma huella. Para afirmar
el commit desplegado con certeza absoluta todavía hace falta consultar Coolify o
el VPS en modo lectura.

## Hallazgo de seguridad

Producción todavía publica `POST /debug` en OpenAPI y Swagger. La versión local
`b491bc5` retiró esa ruta y posee una prueba de regresión que exige `404`.

No se invocó el endpoint productivo para evitar registrar o introducir datos en
los logs. Tampoco se aplicó el cambio local a producción.

## Comparación de Dockerfiles

La rama productiva usa el archivo `Dockerfile`. La rama de integración conserva
la copia histórica con el nombre `Dockerfile.txt`.

- Blob Git de ambos archivos:
  `c5981ef504dd311d959fd409ab093213f425c37e`.
- SHA-256 de ambos contenidos:
  `9d6c1d26167c1dbd48a053f7752129d84f0f15b199a3cc2bc15576b34b639b24`.
- Son idénticos byte por byte.

`Dockerfile.test` mantiene la misma imagen base, instalación de dependencias,
copia de `main.py` y comando Uvicorn. Sólo agrega:

- `PYTHONDONTWRITEBYTECODE=1`;
- `PYTHONUNBUFFERED=1`;
- `EXPOSE 8000`.

Estas diferencias no cambian HTML, CSS, WordPress ni el aspecto visual del sitio.
`EXPOSE` documenta el puerto de la imagen, pero no publica puertos por sí mismo.

## Límites de esta auditoría

Sin una entrada documentada a Coolify o al VPS no se verificaron todavía:

- hash o etiqueta exacta de la imagen en ejecución;
- fecha de creación y configuración del contenedor;
- variables de entorno, mostrando únicamente nombres y nunca valores;
- versión del esquema PostgreSQL;
- ubicación y persistencia efectiva de uploads;
- procedimiento actual de despliegue y reversión.

## Próximo paso seguro

Obtener o documentar el acceso de solo lectura a Coolify/VPS y consultar:

1. identificación del contenedor o servicio;
2. imagen, etiqueta y fecha de creación;
3. origen Git y commit, si Coolify lo registra;
4. nombres de variables requeridas sin revelar valores;
5. montajes y volúmenes sin leer datos personales;
6. estado de salud y logs técnicos mínimos, sin extraer payloads.

No aplicar el commit local, no retirar `/debug` de producción y no reiniciar
servicios hasta contar con respaldo verificable, comprobaciones posteriores,
reversión y autorización expresa.
