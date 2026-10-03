# Decisión de sincronización con GitHub

El repositorio local y el repositorio remoto tienen historiales independientes.

No se hará un merge automático. El `main.py` local contiene toda la
funcionalidad del remoto y no existen rutas exclusivas en la versión remota.

Se adopta el repositorio local como base técnica para el desarrollo futuro. El
repositorio remoto queda como referencia histórica y productiva.

Antes de publicar se deberá validar:

- La suite de tests.
- El contrato de integración con CF7.
- La exposición y el comportamiento de `/debug`.
- La definición y el nombre de `Dockerfile`.
- La versión que se encuentra realmente desplegada en producción.

No se debe ejecutar `pull` ni hacer un merge directo entre ambos historiales.

La sincronización futura será manual, revisada y controlada.
