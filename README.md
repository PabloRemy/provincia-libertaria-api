# Provincia Libertaria API

Backend territorial de Provincia Libertaria. La aplicación usa FastAPI y
PostgreSQL; WordPress y Contact Form 7 funcionan como frontend para los flujos
de reclutamiento y reportes.

## Estado de ramas

- `main`: rama productiva. El release `e9a9b0627a9de12ffa4a05fb6ceeec5dab066dce`
  está desplegado y verificado en `https://mapa.provincialibertaria.com`.
- `integracion-local-sobre-github`: rama de desarrollo y reorganización. Es la
  fuente de verdad técnica para el trabajo futuro y contiene documentación,
  tests, entorno local aislado y un `main.py` más avanzado.

Ambas ramas partieron de historiales independientes. El commit productivo de
reconciliación conserva `abc9807` como padre inmediato y reproduce exactamente
el árbol técnico de `c7c19af`. No ejecutar `pull`, merge ni rebase automático
entre ellas; futuras publicaciones requieren revisión y autorización propias.

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
