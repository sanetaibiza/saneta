/* ==========================================================================
   SA NETA · VARIABLES EDITABLES
   --------------------------------------------------------------------------
   Este es el único archivo que hay que tocar para cambiar los datos de
   contacto. Al guardar, el cambio se aplica en toda la web (cabecera,
   contacto, pie, botón de WhatsApp, barra inferior del móvil y páginas
   legales).
   ========================================================================== */

const COMPANY_NAME = "SA NETA";

const COMPANY_SUBTITLE = "LIMPIEZA PROFESIONAL";

const TAGLINE = "Tu espacio más limpio, más tuyo.";

/* El eslogan en la versión en inglés de la web (carpeta en/). */
const TAGLINE_EN = "Your space, cleaner and truly yours.";

const EMAIL = "sanetaibiza@gmail.com";

/* TELÉFONO — todavía sin definir.
   Cuando exista, sustituir por el número real con prefijo internacional
   (+34 seguido del número). Mientras siga entre corchetes, los botones
   LLAMAR llevan al formulario de contacto en lugar de marcar. */
const PHONE = "[TELÉFONO SA NETA]";

/* WHATSAPP — todavía sin definir.
   Mientras siga entre corchetes, WhatsApp no funciona: los botones se ven,
   pero llevan al formulario de contacto en lugar de abrir WhatsApp.
   Cuando exista, sustituir por el número real con prefijo internacional:
   la web genera sola el enlace https://wa.me/… */
const WHATSAPP = "[WHATSAPP SA NETA]";

const LOCATION = "Ibiza, Illes Balears";

/* DIRECCIÓN DE LA WEB — ahora, la provisional de GitHub.
   Al pasar a un dominio propio, escribir aquí la dirección completa, sin
   barra final (https://www.…). Se usa para completar los datos estructurados. */
const SITE_URL = "https://sanetaibiza.github.io/saneta";

/* Mensaje que aparece ya escrito al abrir WhatsApp. */
const WHATSAPP_MESSAGE = "Hola, me gustaría solicitar un presupuesto de limpieza.";

/* El mismo mensaje para quien escribe desde la versión en inglés. */
const WHATSAPP_MESSAGE_EN = "Hello, I would like to request a cleaning quote.";

/* --------------------------------------------------------------------------
   ENVÍO DEL FORMULARIO DE PRESUPUESTO
   --------------------------------------------------------------------------
   El formulario se envía con el servicio gratuito FormSubmit, que reenvía
   cada solicitud al correo indicado al final de esta dirección. Al terminar,
   la web muestra el mensaje de agradecimiento.

   · La primera vez hay que activar el correo: se envía el formulario una vez
     y se pulsa el botón de activación del email que manda FormSubmit.
   · Para cambiar el correo de destino, cambiar la parte final de la dirección.
   · Con FORM_ENDPOINT vacío ("") no se usa ningún servicio: al pulsar
     SOLICITAR PRESUPUESTO se abre el correo del visitante con la solicitud
     ya redactada.
   · Sirve también la dirección de otro servicio de formularios (Formspree,
     Basin…): la web envía los campos por POST en formato JSON.
   -------------------------------------------------------------------------- */
const FORM_ENDPOINT = "https://formsubmit.co/ajax/sanetaibiza@gmail.com";

/* --------------------------------------------------------------------------
   OPINIONES DE CLIENTES
   --------------------------------------------------------------------------
   Añadir aquí únicamente opiniones reales. Ejemplo de formato:

   const TESTIMONIALS = [
     { text: "Texto de la opinión", name: "Nombre del cliente", stars: 5 },
   ];

   Mientras la lista esté vacía, la sección de opiniones no se muestra.
   En cuanto haya al menos una opinión real, aparece sola.
   -------------------------------------------------------------------------- */
const TESTIMONIALS = [];

const SHOW_TESTIMONIALS = true;

/* --------------------------------------------------------------------------
   GALERÍA
   --------------------------------------------------------------------------
   Oculta mientras solo haya ilustraciones provisionales. Cuando las imágenes
   galeria-1.webp … galeria-6.webp de assets/img/ sean fotografías reales,
   poner SHOW_GALLERY = true.
   -------------------------------------------------------------------------- */
const SHOW_GALLERY = false;

/* No modificar a partir de aquí. */
window.SA_NETA = {
  COMPANY_NAME, COMPANY_SUBTITLE, TAGLINE, TAGLINE_EN, EMAIL, PHONE, WHATSAPP, LOCATION,
  WHATSAPP_MESSAGE, WHATSAPP_MESSAGE_EN, FORM_ENDPOINT, TESTIMONIALS, SHOW_TESTIMONIALS, SHOW_GALLERY, SITE_URL,
};
