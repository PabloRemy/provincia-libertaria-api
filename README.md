# Provincia Libertaria API

Backend territorial de Provincia Libertaria. La aplicación usa FastAPI y
PostgreSQL; WordPress y Contact Form 7 funcionan como frontend para los flujos
de reclutamiento y reportes.

## Estado de ramas

- `main`: rama productiva y referencia histórica en GitHub. Producción continúa
  desplegada desde GitHub, pero el commit efectivamente ejecutado en el VPS debe
  verificarse antes de publicar cambios.
- `integracion-local-sobre-github`: rama de desarrollo y reorganización. Es la
  fuente de verdad técnica para el trabajo futuro y contiene documentación,
  tests, entorno local aislado y un `main.py` más avanzado.

Ambas ramas tienen historiales independientes. No ejecutar `pull`, merge ni
rebase automático entre ellas. La futura sincronización debe ser manual,
revisada y controlada.

## Inicio rápido

Leer, en este orden:

1. `CONTINUAR_DESDE_AQUI.md`
2. `ESTADO_ACTUAL.md`
3. `DECISION_SINCRONIZACION_GITHUB.md`
4. `00_PROVINCIA_LIBERTARIA_MASTER.md`
5. `01_DESARROLLO_TECNICO.md`
6. `02_MAPA_DE_RUTA_ENTORNO_DE_PRUEBAS.md`
7. `README_TESTS.md`

Las instrucciones para levantar el entorno aislado y ejecutar la suite están
en `README_TESTS.md`. Usar solamente credenciales y datos ficticios; la base de
integración debe terminar en `_test`.

## Regla de producción

No hacer despliegues, migraciones ni pruebas contra producción sin autorización
expresa, respaldo verificable y procedimiento de reversión. Antes de preparar
una publicación se debe identificar el commit realmente desplegado, comparar
los estados y validar tests, contrato CF7, `/debug` y Dockerfile.
