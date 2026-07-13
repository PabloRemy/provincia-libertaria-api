# Continuar desde aquí

Actualizado: 2026-07-13.

## Punto de partida verificado

- Repositorio: `https://github.com/PabloRemy/provincia-libertaria-api.git`.
- Clon local: `/home/desk/Documentos/Proyectos/provincia-libertaria-api`.
- Rama activa de desarrollo: `integracion-local-sobre-github`.
- Commit al iniciar esta actualización documental: `0eafb96`.
- La rama local coincide con `origin/integracion-local-sobre-github` y el árbol
  estaba limpio antes de esta actualización.
- Rama productiva: `main`; `origin/main` está en `abc9807`.
- Producción continúa desplegada desde GitHub, pero falta identificar en modo
  lectura qué commit exacto ejecuta actualmente el VPS.

## Decisión de sincronización

`main` e `integracion-local-sobre-github` tienen historiales independientes y
no poseen ancestro común. No ejecutar `pull`, merge ni rebase automático entre
ellas. `main` conserva la referencia productiva e histórica;
`integracion-local-sobre-github` es la fuente de verdad técnica para desarrollo.

La rama de integración contiene documentación, tests, un entorno local aislado
con datos ficticios y un `main.py` más avanzado. La sincronización futura debe
ser manual, revisada y controlada.

## Estado de trabajo

- Entorno local de FastAPI, PostgreSQL, WordPress y MySQL definido en
  `compose.test.yml`.
- Suite automatizada disponible en `tests/`; el último estado documentado prevé
  29 pruebas sin PostgreSQL y 30 con PostgreSQL, pero debe volver a ejecutarse
  para verificar el resultado actual.
- Webhook directo y envío CF7 local sin foto documentados como validados.
- La carga de imagen desde CF7 local sigue registrada como incidencia no
  bloqueante; la API directa sí fue validada.
- No se comparó todavía la rama de integración con el código efectivamente
  desplegado ni existe un procedimiento probado de publicación, respaldo y
  reversión.

## Próximo paso exacto

1. Revisar `README_TESTS.md` y levantar sólo el entorno local aislado.
2. Ejecutar la suite sin PostgreSQL y luego la suite completa; registrar el
   resultado real.
3. Validar el contrato WordPress/CF7, la exposición de `/debug` y la definición
   de Dockerfile.
4. Identificar en producción, en modo lectura, el commit o contenido exacto
   desplegado y compararlo con la rama de integración.
5. Preparar un procedimiento manual de publicación con respaldo,
   comprobaciones posteriores y reversión.

No modificar producción, no integrar historiales y no desplegar sin autorización
expresa.
