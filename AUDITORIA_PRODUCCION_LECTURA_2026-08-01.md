# Auditoría de producción en modo lectura — 2026-08-01

## Alcance y seguridad de la auditoría pública inicial

La primera etapa se realizó exclusivamente mediante consultas públicas y
comandos Git locales de lectura. En esa etapa no se enviaron formularios, no se
ejecutaron solicitudes POST, no se accedió a bases de datos y no se modificaron
archivos del VPS.

Las etapas SSH posteriores instalaron y actualizaron únicamente el script de
auditoría restringida, conservando copias reversibles. Ese script consultó
metadatos del contenedor, filesystem y estructura PostgreSQL en una conexión
marcada `READ ONLY`. En ninguna etapa se reiniciaron ni desplegaron servicios,
se modificaron datos de negocio o se alteró el sitio público.

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

## Auditoría ampliada — versión 2

El comando restringido fue ampliado y verificado desde Desk. La copia versionada
se encuentra en `scripts/provincia-audit-readonly`; el archivo instalado en el
VPS posee SHA-256:

`ff04844112a9904bf0763f196f8ebdf46b347f6bf4292c21a7e97170440cfdab`

Durante la instalación se conservó la versión anterior en
`/root/provincia-audit-readonly.v1.20260801`. La primera ejecución de la versión
2 se interrumpió después de enumerar variables porque `pipefail` propagó el
estado de una última línea vacía. No alcanzó las consultas de `/data` ni de base.
La condición fue corregida, validada por hash y ejecutada nuevamente con éxito.

Una revisión independiente posterior detectó que serializar entradas completas
`KEY=VALUE` antes de recortar el nombre podía filtrar parte de un valor
multilínea. La versión final obtiene directamente `os.environ.keys()` dentro del
contenedor, sin imprimir valores. La misma revisión señaló que los errores de
PostgreSQL no debían terminar con estado exitoso: ahora la ausencia de
`DATABASE_URL` devuelve código 20 y cualquier fallo genérico de conexión o
consulta devuelve código 21, manteniendo ocultos los detalles sensibles.

La versión final fue instalada mediante un parche con simulación previa,
conservando la versión 2 en
`/root/provincia-audit-readonly.v2.20260801`. La ejecución remota posterior
terminó con código 0 y el informe completo.

### Configuración requerida

Se enumeraron sólo nombres de variables; ningún valor fue extraído. Las variables
relevantes de la aplicación y Coolify incluyen:

- `ADMIN_USERS`;
- `DATABASE_URL`;
- `COOLIFY_BRANCH`;
- `COOLIFY_CONTAINER_NAME`;
- `COOLIFY_FQDN`;
- `COOLIFY_RESOURCE_UUID`;
- `COOLIFY_URL`;
- `SOURCE_COMMIT`;
- `HOST` y `PORT`.

También existen variables propias de la imagen oficial de Python. Su presencia
no implica que sea necesario copiarlas a documentación o configuración local.

### Persistencia de imágenes

- Origen del bind mount: `/data/incidentes-fotos`.
- Destino dentro del contenedor: `/data`.
- Tamaño observado: 2.072.952 bytes, aproximadamente 1,98 MiB.
- Archivos: 28.
- Directorios: 3.
- Última modificación observada: 2026-06-30 02:22:05 UTC.
- Filesystem: aproximadamente 95,82 GiB totales y 71,05 GiB disponibles; uso
  informado del 26 %.

No se mostraron nombres ni contenido de archivos. Estos metadatos prueban la
persistencia actual, pero no prueban la existencia de una copia de respaldo.

### Esquema PostgreSQL productivo

La consulta se ejecutó dentro del contenedor mediante una conexión PostgreSQL
marcada `READ ONLY` y consultó exclusivamente `information_schema`. No se
consultaron filas de negocio.

- Esquema: `public`.
- Tablas: `incidentes` y `reclutamiento_registros`.
- Columnas totales: 25.

Diferencias observadas frente a `sql/test_schema.sql`:

1. Producción incluye `reclutamiento_registros.origen`; el esquema local no.
2. Los identificadores productivos aparecen como `integer`; el esquema local
   declara `BIGSERIAL`.
3. `incidentes.ciudad`, `barrio` y `categoria` aparecen como
   `character varying`; local los declara `TEXT`.
4. `incidentes.latitud` y `longitud` aparecen como `numeric`; local usa
   `DOUBLE PRECISION`.
5. En producción `incidentes.estado`, `fecha_reporte` y `fecha_actualizacion`
   admiten nulos según `information_schema`; local los declara `NOT NULL`.
6. En producción `reclutamiento_registros.fecha_registro` admite nulos; local lo
   declara `NOT NULL`.

Esta auditoría no consultó defaults, constraints, índices ni secuencias. Por eso
no corresponde preparar una migración hasta completar esa comparación.

## Límites de esta auditoría

Todavía no se verificaron:

- defaults, constraints, índices y secuencias PostgreSQL;
- existencia, frecuencia e integridad de respaldos de base y uploads;
- procedimiento actual de despliegue y reversión en Coolify.

## Próximo paso seguro

1. Extender la consulta estructural a defaults, constraints, índices y
   secuencias, sin consultar filas.
2. Identificar en Coolify la configuración de respaldos sin mostrar secretos.
3. Diseñar y ensayar un respaldo verificable antes de cualquier despliegue.
4. Documentar comprobaciones posteriores y reversión.

No aplicar el commit local, no retirar `/debug` de producción y no reiniciar
servicios hasta contar con respaldo verificable, comprobaciones posteriores,
reversión y autorización expresa.
