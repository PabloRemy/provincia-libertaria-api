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
corresponde a `origin/main`. La consulta posterior al contenedor confirmó además
que la imagen desplegada está etiquetada con el commit completo
`abc9807bba2974ecd1bab36aa80166de3c66fbdf`.

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

## Acceso SSH restringido verificado

Se creó en el VPS el usuario `auditor_pl`, sin contraseña operativa y sin
pertenencia al grupo `docker`. La clave autorizada tiene `restrict` y un comando
forzado. El único `sudo` permitido es:

`/usr/local/sbin/provincia-audit-readonly`

El script pertenece a `root`, no es modificable por el auditor y devuelve sólo
metadatos filtrados. No muestra variables de entorno ni contenido de volúmenes.
Desde Desk se configuró el alias local `provincia-vps-auditoria` con una clave
dedicada que no se guarda en el repositorio.

Se verificó que:

- la conexión funciona sin contraseña;
- el usuario no recibe una terminal interactiva;
- al solicitar otro comando, por ejemplo `id`, el servidor lo ignora y ejecuta
  nuevamente el informe fijo;
- el acceso no permite despliegues, reinicios ni comandos Docker arbitrarios.

## Contenedor productivo confirmado

- Servidor: `srv886973`.
- Contenedor: `n85p5qn4eo94demg4mnbfu3m-132351845310`.
- Imagen: `n85p5qn4eo94demg4mnbfu3m:abc9807bba2974ecd1bab36aa80166de3c66fbdf`.
- ID de imagen: `sha256:5ab53fcf30b144d908880375d8e8615dcbe8d8a9ee45e0262d67fdcb0f2e57a5`.
- Creado e iniciado: 2026-06-19.
- Estado observado: en ejecución, sin reinicios registrados.
- Política de reinicio: `unless-stopped`.
- Montaje: bind hacia `/data`, con escritura habilitada para la aplicación.
- Sistema de imagen: `linux/amd64`.

El permiso de escritura del montaje corresponde al contenedor productivo; no
implica que el usuario auditor pueda escribir en `/data`.

## Límites de esta auditoría

Todavía no se verificaron:

- nombres de variables requeridas, sin mostrar valores;
- versión del esquema PostgreSQL;
- persistencia efectiva y respaldo de uploads;
- procedimiento actual de despliegue y reversión.

## Próximo paso seguro

Antes de ampliar la auditoría, decidir explícitamente si el comando restringido
debe incorporar nuevas consultas. Las próximas candidatas son:

1. nombres de variables requeridas sin revelar valores;
2. versión y estructura del esquema PostgreSQL sin consultar filas;
3. estado de respaldo de `/data` sin leer datos personales;
4. procedimiento de despliegue y reversión en Coolify.

No aplicar el commit local, no retirar `/debug` de producción y no reiniciar
servicios hasta contar con respaldo verificable, comprobaciones posteriores,
reversión y autorización expresa.
