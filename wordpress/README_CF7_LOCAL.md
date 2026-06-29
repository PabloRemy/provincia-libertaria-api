# Contact Form 7 local

## Formulario

- Nombre: `Reporte de barrio local`.
- Contenido: `cf7-formulario-reporte.txt`.
- El barrio, la dirección, la foto y el GPS son opcionales.

## Webhook

La URL se resuelve dentro de la red privada de Docker:

```text
http://api-test:8000/incidente-foto-json
```

No usar la URL pública en el entorno local.

## Correo

El entorno local no debe enviar correos reales. En la pestaña de ajustes
adicionales de Contact Form 7 usar:

```text
skip_mail: on
```

## JavaScript

Durante la primera prueba no agregar el script productivo de redirecciones: sus
destinos pertenecen al sitio público. La captura de GPS se validará por separado.
