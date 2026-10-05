# SA NETA · Limpieza profesional — web

Web one page en HTML, CSS y JavaScript, sin librerías ni dependencias. Se publica subiendo esta carpeta tal cual a cualquier hosting.

## Estructura

```
index.html                  Página principal (todas las secciones)
aviso-legal.html            Textos legales (faltan titular, NIF/CIF y domicilio)
404.html                    Página de error para direcciones que no existen
politica-privacidad.html
politica-cookies.html
css/styles.css              Estilos (colores y tipografías al principio del archivo)
js/config.js                VARIABLES EDITABLES: contacto, formulario, opiniones
js/main.js                  Menú, animaciones, formulario
assets/logo-oficial.png     Logo oficial (original, sin modificar)
assets/logo-360.webp / logo-720.webp   Logo optimizado para la web
assets/img/                 Imágenes (ahora provisionales)
assets/fonts/               Tipografías Playfair Display y Montserrat (licencia SIL Open Font License)
assets/og-image.jpg         Imagen al compartir en WhatsApp, Facebook, etc.
favicon.ico, assets/favicon-32.png, assets/apple-touch-icon.png, assets/icon-*.png
robots.txt, sitemap.xml, site.webmanifest
tools/                      Utilidades de desarrollo (no hace falta subirlas)
```

## 1. Datos de contacto → `js/config.js`

Todas las variables están en un único archivo:

```js
const COMPANY_NAME = "SA NETA";
const COMPANY_SUBTITLE = "LIMPIEZA PROFESIONAL";
const TAGLINE = "Tu espacio más limpio, más tuyo.";
const EMAIL = "sanetaibiza@gmail.com";
const PHONE = "[TELÉFONO SA NETA]";
const WHATSAPP = "[WHATSAPP SA NETA]";
const LOCATION = "Ibiza, Illes Balears";
```

**Teléfono.** Mientras siga entre corchetes, la web muestra el texto `[TELÉFONO SA NETA]` y los botones LLAMAR llevan al formulario de contacto. Al escribir el número real en `PHONE`, pasa a ser un enlace `tel:` en la barra superior, el menú móvil, contacto, el pie y la barra inferior del móvil.

**WhatsApp.** Los botones (flotante en ordenador y barra inferior en móvil) se ven, pero mientras `WHATSAPP` siga entre corchetes no abren WhatsApp: llevan al formulario de contacto. Al escribir el número real abren `https://wa.me/<número>` con el mensaje de `WHATSAPP_MESSAGE`.

El email y el teléfono también aparecen en el bloque de datos estructurados de `index.html` (`<script type="application/ld+json">`); cuando haya teléfono se puede añadir ahí una línea `"telephone": "…"`.

## 2. Formulario de presupuesto → `FORM_ENDPOINT`

No hay ningún sistema de envío inventado:

- **Sin configurar** (`FORM_ENDPOINT = ""`): al pulsar SOLICITAR PRESUPUESTO se valida el formulario y se abre la aplicación de correo del visitante con la solicitud ya redactada para `sanetaibiza@gmail.com`. Funciona en cualquier hosting, pero depende de que el visitante tenga el correo configurado en su dispositivo.
- **Con servicio de formularios** (recomendado para publicar): pegar en `FORM_ENDPOINT` la URL que proporcione el servicio elegido (Formspree, Basin, Netlify Forms, un script del propio hosting…). La web envía los campos por POST en JSON: `nombre`, `telefono`, `email`, `tipo_servicio`, `zona`, `frecuencia`, `mensaje`.

## 3. Fotografías → `assets/img/`

| Archivo | Dónde aparece | Formato recomendado |
|---|---|---|
| `rama-olivo.webp` (y `rama-olivo-420.webp`, la misma a 420 px de ancho) | Portada: ramas de olivo en las dos esquinas superiores | PNG o WebP con fondo transparente, con las ramas entrando desde la esquina superior izquierda |
| `equipo.webp` y `equipo-480.webp` | Sobre nosotros, foto del equipo | Vertical 2:3, 800 × 1200 px y 480 × 720 px |
| `servicio-viviendas.webp`, `servicio-oficinas-locales.webp`, `servicio-cristales.webp`, `servicio-urgencias.webp` (y cada una en dos tamaños menores, terminadas en `-480.webp` y `-320.webp`) | Tarjetas de servicios | 800 × 760 px, 480 × 456 px y 320 × 304 px |
| `galeria-1.webp` … `galeria-6.webp` | Galería (ahora oculta) | Horizontal, 1200 × 900 px |

Las ramas de la portada son un recorte ampliado del flyer; conviene sustituirlas por la fotografía original en alta resolución, con el mismo nombre.

**Fotos de los servicios.** Cada tarjeta muestra su fotografía en el arco y su icono en un sello redondo sobre el borde inferior de la foto (en móvil, una tarjeta por fila). Origen de cada una:

- Viviendas, Oficinas y locales, Cristales y Urgencias: recortes del collage facilitado por SA NETA (unos 500 px de ancho, ampliados a 800).
- Sobre nosotros: imagen vertical facilitada por SA NETA (profesional aspirando un salón).

Para cambiar una foto, sustituir los tres archivos (grande, `-480` y `-320`) con el mismo nombre.

**Galería.** Está oculta porque sus seis imágenes son ilustraciones provisionales. Cuando sean fotografías reales (mismos nombres de archivo), poner `SHOW_GALLERY = true` en `js/config.js`.

Conviene que cada foto pese menos de 250 KB. Si cambia el contenido de una imagen, actualizar su texto `alt` en `index.html`.

## 4. Opiniones de clientes → `TESTIMONIALS`

La sección está oculta mientras no haya opiniones reales. Al añadir la primera en `js/config.js`, aparece sola:

```js
const TESTIMONIALS = [
  { text: "Texto de la opinión", name: "Nombre del cliente", stars: 5 },
];
```

## 5. Antes de publicar

1. Sustituir `[URL WEB]` por la dirección real, sin barra final (por ejemplo `https://www.midominio.es`), en `index.html` (canonical, Open Graph, Twitter), `js/config.js` (`SITE_URL`), `robots.txt` y `sitemap.xml`.
2. Escribir teléfono y WhatsApp en `js/config.js`.
3. Decidir el envío del formulario (`FORM_ENDPOINT`).
4. Sustituir las fotos del flyer por las originales y, cuando haya fotos reales, activar la galería.
5. Completar los tres datos `[POR DEFINIR]` de las páginas legales (titular, NIF/CIF y domicilio) y revisarlas con un asesor. Al entrar en la web aparece un aviso con enlace a las tres páginas, que desaparece al pulsar Aceptar; el formulario exige aceptar la política de privacidad y el aviso legal.

**Datos estructurados.** `index.html` lleva un bloque JSON-LD (`LocalBusiness`) solo con datos reales: nombre, eslogan, email, zona (Ibiza y sus municipios) y los servicios. La dirección de la web, el logo y el teléfono se añaden solos cuando `SITE_URL` y `PHONE` dejan de estar entre corchetes. No incluye dirección postal, horarios ni valoraciones.

## 6. Publicar

Subir todo el contenido de esta carpeta (menos `tools/` y este README) a la raíz del hosting. Sirve cualquier alojamiento de páginas estáticas. La web no usa cookies de seguimiento ni carga nada de servidores externos; solo recuerda en el navegador que el visitante ha aceptado el aviso.

## Mantenimiento

- **Colores y tipografías:** variables al inicio de `css/styles.css` (`--navy`, `--sky`, `--sky-light`…), según el flyer y la identidad visual de SA NETA.
- **Textos:** directamente en `index.html`; cada sección está señalada con un comentario numerado.
- **Regenerar las ilustraciones provisionales de la galería:** `python3 tools/make_images.py` (requiere Python con Pillow y Playwright).


**Logo de la portada.** La portada y la cabecera usan `assets/logo-simple-720.webp` y `logo-simple-360.webp`: el logo oficial con el dibujo y el nombre, sin la línea «Limpieza profesional» (esa frase va escrita justo debajo, como «Limpieza profesional en Ibiza»). El logo completo sigue en el pie de página (`assets/logo-720.webp`).
