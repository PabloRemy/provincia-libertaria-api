# Contact Form 7 local

Validado extremo a extremo el 14 de julio de 2026. Este documento describe sólo
el entorno local; producción no fue validada ni modificada.

## Formulario

- Nombre: `Reporte de barrio local`.
- Shortcode: `[contact-form-7 id="44e0661" title="Reporte de barrio local"]`.
- Contenido: `cf7-formulario-reporte.txt`.
- El barrio, la dirección, la foto y el GPS son opcionales.
- PHP local admite archivos de hasta 4 MB; CF7 limita las fotos a 3 MB.

## Webhook

El webhook lo gestiona el mu-plugin versionado
`mu-plugins/provincia-libertaria-cf7-local.php`. No se requiere ni se instaló un
plugin externo de webhooks. La URL se resuelve dentro de la red privada Docker:

```text
http://api-test.local:8000/incidente-foto-json
```

No usar la URL pública en el entorno local.

## Correo

El entorno local no debe enviar correos reales. En la pestaña de ajustes
adicionales de Contact Form 7 usar:

```text
skip_mail: on
```

El entorno local fue validado sin envío de correos.

## Resultado validado

- Envío sin foto: incidente persistido con `foto_url` vacío, como corresponde.
- Envío con foto: JPG recibido, convertido a WebP, persistido y visible mediante
  `/foto/{nombre}` y en el panel de Berisso.
- WordPress, formulario, incidente y archivo WebP persistieron después de
  detener Compose sin `-v` y volver a levantarlo.

La incidencia anterior de carga de imagen local ya no se reproduce. No inferir
de este resultado que producción usa el mismo código o configuración.

## JavaScript

No agregar el script productivo de redirecciones: sus destinos pertenecen al
sitio público. La captura de GPS se valida por separado.
