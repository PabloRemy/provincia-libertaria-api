# Mapa de ruta — Entorno de pruebas

Última actualización: 30 de junio de 2026.

## Instrucción para futuras sesiones de Codex

Leer, en este orden:

1. `00_PROVINCIA_LIBERTARIA_MASTER.md`
2. `01_DESARROLLO_TECNICO.md`
3. Este documento.
4. `README_TESTS.md`

Antes de modificar archivos, comprobar el estado real del proyecto y ejecutar
la suite de pruebas. No tocar el VPS ni producción sin autorización expresa,
respaldo y un procedimiento de reversión.

## Objetivo

Construir en la computadora local una réplica segura y suficientemente fiel de
Provincia Libertaria para desarrollar y probar cambios antes de publicarlos en
el VPS.

El entorno local debe usar datos ficticios y recursos aislados. Nunca debe
conectarse accidentalmente a la base de datos productiva.

## Arquitectura prevista

### Entorno local

- FastAPI local.
- PostgreSQL de pruebas en Docker.
- Archivos subidos en un directorio temporal local.
- Usuarios y contraseñas ficticios.
- Pruebas automáticas y revisión visual en navegador.

### Producción

- WordPress como frontend.
- FastAPI como backend.
- PostgreSQL real.
- Docker, Coolify y VPS Hostinger.
- Datos y usuarios reales.

Los entornos deben permanecer separados.

## Criterio de trabajo

En local debe seguir avanzando todo lo que sea backend, base de datos, tablero,
paneles, eventos, reclutamiento, filtros, exportables y refactor interno. La
idea es validar cambios de forma segura antes de llevarlos a producción.

El formulario de reportes se está ajustando directamente en producción, con
cambios chicos y reversibles, porque ahí funciona el flujo real con WordPress,
CF7, webhook e imágenes. La incidencia de imagen en CF7 local no debe bloquear
el avance del resto del proyecto.

Toda mejora local que se quiera llevar a producción debe pasar por comparación,
respaldo y plan de reversión.

## Estado actual

### Completado

- Entorno virtual Python `.venv`.
- Dependencias de desarrollo en `requirements-dev.txt`.
- Configuración de pytest en `pytest.ini`.
- Pruebas de página principal, normalización y ciudades.
- Pruebas de autenticación y permisos territoriales.
- Prueba de integración con PostgreSQL.
- Esquema descartable en `sql/test_schema.sql`.
- Docker Engine y Docker Compose instalados en la computadora.
- PostgreSQL 16 de pruebas definido en `compose.test.yml`.
- WordPress 6.9.4 y MySQL 8.4 locales definidos en `compose.test.yml`.
- WordPress local instalado en `http://127.0.0.1:8080`.
- Plugins Contact Form 7 y CF7 to Webhook instalados y activados localmente.
- Plantilla local del formulario guardada en `wordpress/`.
- Endpoint local de diagnóstico de WordPress verificado:
  `/?rest_route=/provincia-libertaria/v1/cf7-local` responde `ok: true`.
- Webhook directo de FastAPI verificado con reporte `id=14`.
- Envío completo desde WordPress local con CF7 verificado con reporte `id=15`.
- `skip_mail` está forzado por el mu-plugin local y puede mantenerse además en
  Ajustes adicionales de CF7.
- Carga de imagen por Base64 verificada previamente con conversión a WebP y
  persistencia en `foto_url`, reporte `id=11`.
- Prueba desde WordPress local con imagen reprodujo el problema: el reporte
  `id=16` se guardó, pero `foto_url` quedó vacío.
- Mu-plugin local ajustado para enviar el webhook desde
  `wpcf7_before_send_mail`, después de que CF7 prepara los archivos subidos.
- Mu-plugin local reforzado con diagnóstico de carga de foto y fallback a
  `$_FILES['foto']` si `WPCF7_Submission::uploaded_files()` no informa la ruta.
- Decisión: no seguir bloqueando el proyecto por la carga de imagen desde CF7
  local. En producción el formulario funciona correctamente; el caso local queda
  registrado como incidencia no bloqueante del entorno de pruebas.
- Producción: se probó una mejora de UX del formulario de reportes con `barrio`
  opcional y mensajes claros para campos obligatorios. El reporte se envió
  correctamente, pero el flujo fue lento y requirió varios intentos.
- Puerto publicado sólo en `127.0.0.1:55432`.
- Base `provincia_libertaria_test` protegida mediante sufijo `_test`.
- Suite sin PostgreSQL verificada: 29 pruebas aprobadas.
- Suite completa prevista con PostgreSQL local activo: 30 pruebas.

### Todavía no realizado

- No se probó la aplicación completa desde el navegador.
- La carga de imagen desde CF7 local queda como incidencia no bloqueante del
  entorno de pruebas; producción funciona correctamente y la API directa ya
  valida conversión y persistencia.
- Falta validar el formulario de reclutamiento desde WordPress local.
- Falta revisar la lentitud/fricción del formulario productivo de reportes tras
  la mejora de UX, sin cambiar todavía la lógica de backend.
- No se comparó la copia local con la versión actualmente desplegada en el VPS.
- No existe todavía un procedimiento de publicación, respaldo y reversión.

## Comandos habituales

Ubicación del proyecto:

```bash
cd /home/lab/Documentos/provincialibertaria/provincia-libertaria-api
```

Levantar PostgreSQL de pruebas:

```bash
sudo docker compose -f compose.test.yml up -d --wait
```

Preparar las variables locales, si `.env.test` todavía no existe:

```bash
cp .env.test.example .env.test
```

Ejecutar todas las pruebas:

```bash
set -a
source .env.test
set +a
.venv/bin/pytest -q
```

Resultado esperado con PostgreSQL local activo:

```text
30 passed
```

Detener PostgreSQL conservando el volumen:

```bash
sudo docker compose -f compose.test.yml down
```

Detener PostgreSQL y eliminar todos sus datos descartables:

```bash
sudo docker compose -f compose.test.yml down -v
```

## Mapa de ruta

### Principio de producto

Provincia Libertaria debe seguir siendo una herramienta liviana: rápida de
usar, simple de mantener y enfocada en captar información territorial real sin
ponerle fricción innecesaria a la gente. Las mejoras técnicas, incluida la futura
separación de `main.py` en módulos, deben hacerse de forma incremental y sin
convertir el sistema en una plataforma pesada.

Decisión al 30 de junio de 2026: ordenar `main.py` en la próxima sesión, antes
de sumar eventos, reclutamiento avanzado y tablero versátil. El proyecto todavía
está en fase de prueba y es mejor encarar esta separación ahora, con poco
tránsito, que cuando haya más uso real.

### Backlog de producto

#### Reportes cotidianos

Mantener reportes como herramienta principal para relevar problemas diarios:
basura, iluminación, calles, inseguridad, agua, transporte, salud, burocracia y
otros reclamos vecinales. El campo `barrio` debe seguir siendo opcional y libre
para no bloquear cargas por diferencias de nombres.

#### Eventos territoriales

Agregar una entidad o flujo separado para eventos no cotidianos que conviene
contabilizar en el tiempo. Ejemplos:

- Corte de luz masivo.
- Poste caído.
- Calle cortada.
- Accidente importante.
- Inundación.
- Temporal.
- Incendio.
- Fuga de agua.
- Manifestación.
- Árbol caído.

Definir si el tipo de evento será un selector con categorías base más opción
`Otro`, o un campo libre normalizado después. Recomendación inicial: selector
simple más descripción libre, para conservar orden sin frenar la carga.

#### Tablero territorial versátil

Evolucionar el tablero para poder seleccionar un distrito, varios distritos o la
provincia completa. Agregar filtros por categoría, estado, fecha y tipo de dato.
Ejemplo esperado: si se filtra `Inseguridad`, se apagan los demás pines y quedan
visibles sólo esos casos.

Mejorar la lectura visual de pines por estado:

- Reclamo activo: amarillo.
- Solucionado: verde.
- Sin atención: rojo.

#### Reclutamiento y armadores

El tablero de administración y el perfil `armador` deben mostrar cantidad de
reclutas por distrito y una tabla consultable. Debe permitir elegir Berisso, La
Plata, Ensenada u otros distritos, ver rápidamente los registros de cada uno y
exportarlos.

Campos mínimos esperados: nombre, contacto, ciudad, barrio/zona, participación,
mensaje, fecha de alta y estado de seguimiento.

#### Escucha activa

Incorporar formularios de escucha activa como una encuestadora artesanal: muchos
"oídos virtuales" recogiendo información desde redes, campañas y consultas
puntuales. La lógica es crear preguntas simples, distribuirlas en redes y guardar
respuestas para análisis territorial.

Ejemplos de uso:

- Preguntas abiertas por distrito.
- Encuestas breves sobre servicios públicos.
- Relevamientos de prioridades barriales.
- Formularios temáticos vinculados a campañas.

Esta línea debe pensarse como un tercer flujo junto a reportes y eventos:
reportes para problemas cotidianos, eventos para hechos puntuales relevantes y
escucha activa para opinión, percepción y prioridades.

### Etapa 1 — Punto de restauración local (completada)

1. Revisar archivos sensibles y exclusiones de `.gitignore`.
2. Inicializar un repositorio Git local.
3. Registrar el estado inicial conocido y probado.
4. No publicar todavía el repositorio en ningún servicio externo.

Condición de finalización: existe un punto de restauración local y las pruebas
continúan aprobando.

### Etapa 2 — API local completa (completada)

1. Incorporar FastAPI a `compose.test.yml` o a una configuración local
   equivalente.
2. Conectar exclusivamente con `provincia_libertaria_test`.
3. Usar un directorio local temporal para las imágenes.
4. Agregar comprobaciones de salud para API y PostgreSQL.

Condición de finalización: la API responde localmente sin depender del VPS.

### Etapa 3 — Datos ficticios reproducibles (completada)

1. Crear registros de ejemplo para Berisso, Ensenada y La Plata.
2. Incluir categorías, barrios, estados y coordenadas representativas.
3. Crear usuarios administrativos ficticios con distintos alcances.
4. Automatizar la carga y limpieza de esos datos.

Condición de finalización: cualquier sesión puede reconstruir el mismo escenario
de prueba desde cero.

### Etapa 4 — Validación funcional

1. Probar formularios de reclutamiento y reportes. En progreso: validado el
   webhook directo con reporte `id=14` y validado el envío completo desde
   WordPress local con CF7 con reporte `id=15`, sin foto ni GPS. En producción
   se validó una mejora de UX para reportes, con envío exitoso pero lento.
   Sigue pendiente validar el formulario de reclutamiento.
2. Probar autenticación y restricciones por distrito. Validado: un usuario de
   Berisso obtiene acceso a Berisso y rechazo `403` en Ensenada.
3. Probar carga y visualización de imágenes. Parcialmente validado: por API
   directa funciona con reporte `id=11`, recepción Base64, conversión a WebP,
   persistencia en `foto_url` y entrega HTTP. La prueba desde CF7 local guardó
   el reporte `id=16`, pero sin `foto_url`. Como producción funciona
   correctamente, este punto queda como incidencia local no bloqueante.
4. Probar paneles, mapas, filtros y moderación. Validado: panel distrital,
   publicación de un reporte, vista pública, mapa, marcadores y ventanas de
   detalle.
5. Agregar pruebas automáticas para los defectos encontrados.

Condición de finalización: los recorridos principales funcionan mediante API y
navegador, con evidencia reproducible.

### Etapa 4.5 — Orden interno de `main.py`

Objetivo: reducir el riesgo de seguir creciendo sobre un único archivo central,
manteniendo Provincia Libertaria liviana y sin cambiar comportamiento visible.

Orden sugerido:

1. Ejecutar la suite completa antes de tocar código.
2. Identificar bloques actuales de `main.py`: configuración, modelos, base de
   datos, normalización, autenticación, imágenes, webhooks, vistas públicas,
   paneles y administración.
3. Extraer primero módulos de bajo riesgo:
   - `config.py`
   - `database.py`
   - `models.py`
   - `normalization.py`
   - `auth.py`
   - `images.py`
4. Mantener rutas y HTML en `main.py` al principio, para no mezclar refactor con
   cambios de producto.
5. Ejecutar tests después de cada extracción.
6. Recién después evaluar separar rutas por dominio:
   reportes, reclutamiento, paneles, territorio y webhooks.

Reglas:

- No cambiar URLs públicas.
- No cambiar nombres de campos usados por WordPress/CF7.
- No cambiar esquema de base durante esta etapa.
- No desplegar a producción hasta terminar comparación, respaldo y plan de
  reversión.

Condición de finalización: `main.py` queda más chico, las responsabilidades
principales están separadas y la suite sigue aprobando.

### Etapa 5 — Comparación con producción

1. Identificar exactamente qué versión se ejecuta en el VPS.
2. Comparar configuración, esquema y código sin copiar secretos ni datos reales.
3. Registrar diferencias y migraciones necesarias.
4. Mantener producción en modo de sólo lectura durante este análisis.

Condición de finalización: se conocen las diferencias entre local y producción.

### Etapa 6 — Publicación segura

1. Crear respaldo verificable de base y archivos.
2. Definir migraciones y orden de despliegue.
3. Definir comprobaciones posteriores a la publicación.
4. Definir un procedimiento de reversión.
5. Publicar sólo con autorización expresa.

Condición de finalización: cambio desplegado, verificado y reversible.

## Próximo paso acordado

Próxima sesión: ordenar `main.py` antes de sumar nuevas funcionalidades:

1. Levantar el entorno con
   `sudo docker compose -f compose.test.yml up -d --wait`.
2. Ejecutar la suite local y confirmar el estado actual.
3. Hacer un refactor incremental de `main.py`, empezando por módulos de bajo
   riesgo y sin cambiar comportamiento.
4. Ejecutar tests después de cada extracción.
5. Luego continuar con formulario de reportes, eventos territoriales,
   reclutamiento y tablero.

No agregar todavía el JavaScript productivo de redirecciones porque dirige al
sitio público.

## Reglas de seguridad

- Nunca usar credenciales reales en `.env.test`.
- Nunca apuntar `TEST_DATABASE_URL` a producción.
- Toda base de integración debe terminar en `_test`.
- No subir archivos `.env` al control de versiones.
- No ejecutar migraciones ni despliegues en el VPS sin autorización expresa.
- Antes de publicar: pruebas aprobadas, respaldo y reversión definidos.
