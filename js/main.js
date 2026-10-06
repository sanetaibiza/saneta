/* ==========================================================================
   SA NETA · comportamiento de la web
   Sin librerías externas. Los datos editables están en js/config.js.
   ========================================================================== */
(function () {
  "use strict";

  var cfg = window.SA_NETA || {};
  var root = document.documentElement;
  root.classList.add("js");

  /* Un dato está "pendiente" mientras siga vacío o entre corchetes: [TELÉFONO SA NETA] */
  function isPending(value) {
    return !value || /^\s*\[.*\]\s*$/.test(value);
  }
  function digits(value) {
    return String(value).replace(/[^\d]/g, "");
  }

  /* ---------- 1. Variables de config.js → textos y enlaces ---------- */
  function applyConfig() {
    document.querySelectorAll("[data-var]").forEach(function (el) {
      var value = cfg[el.getAttribute("data-var")];
      if (typeof value === "string" && value) el.textContent = value;
    });

    document.querySelectorAll('[data-link="email"]').forEach(function (a) {
      if (!isPending(cfg.EMAIL)) a.href = "mailto:" + cfg.EMAIL;
    });

    document.querySelectorAll('[data-link="phone"]').forEach(function (a) {
      if (isPending(cfg.PHONE)) {
        a.href = "#contacto";
        a.setAttribute("data-pending", "");
      } else {
        var plus = cfg.PHONE.trim().charAt(0) === "+" ? "+" : "";
        a.href = "tel:" + plus + digits(cfg.PHONE);
        a.removeAttribute("data-pending");
      }
    });

    document.querySelectorAll('[data-link="whatsapp"]').forEach(function (a) {
      if (isPending(cfg.WHATSAPP)) {
        a.href = "#contacto";          /* sin número no abre WhatsApp: lleva al formulario */
        a.removeAttribute("target");
        a.setAttribute("data-pending", "");
      } else {
        var number = digits(cfg.WHATSAPP);
        if (number.length === 9) number = "34" + number; /* número español sin prefijo */
        a.href = "https://wa.me/" + number + "?text=" + encodeURIComponent(cfg.WHATSAPP_MESSAGE || "");
        a.target = "_blank";
        a.rel = "noopener";
        a.removeAttribute("data-pending");
      }
    });

    /* Textos que solo tienen sentido cuando WhatsApp está activo */
    document.querySelectorAll("[data-if-whatsapp]").forEach(function (el) {
      el.hidden = isPending(cfg.WHATSAPP);
    });
  }

  /* ---------- 2. Cabecera: sombra al hacer scroll y menú hamburguesa ---------- */
  function initHeader() {
    var header = document.querySelector(".site-header");
    var toggle = document.querySelector(".menu-toggle");
    var nav = document.getElementById("menu");
    if (!header) return;

    function onScroll() {
      header.classList.toggle("is-scrolled", window.scrollY > 30);
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });

    /* El botón flotante de WhatsApp aparece al pasar la portada (allí ya hay un botón de WhatsApp) */
    var hero = document.querySelector(".hero");
    if (hero && "IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        root.classList.toggle("past-hero", !entries[0].isIntersecting);
      }, { rootMargin: "-40% 0px 0px 0px" }).observe(hero);
    } else {
      root.classList.add("past-hero");
    }

    /* El logo de la cabecera aparece cuando el logo grande de la portada sale de la pantalla */
    var heroLogo = document.querySelector(".hero-logo");
    if (heroLogo && "IntersectionObserver" in window) {
      new IntersectionObserver(function (entries) {
        header.classList.toggle("show-brand", !entries[0].isIntersecting);
      }, { rootMargin: "-80px 0px 0px 0px" }).observe(heroLogo);
    } else {
      header.classList.add("show-brand");
    }

    if (!toggle || !nav) return;
    var label = toggle.querySelector(".sr-only");

    function setOpen(open) {
      toggle.setAttribute("aria-expanded", String(open));
      nav.classList.toggle("is-open", open);
      root.classList.toggle("menu-open", open);
      if (label) label.textContent = open ? "Cerrar menú" : "Abrir menú";
    }
    toggle.addEventListener("click", function () {
      setOpen(toggle.getAttribute("aria-expanded") !== "true");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && toggle.getAttribute("aria-expanded") === "true") {
        setOpen(false);
        toggle.focus();
      }
    });
    window.matchMedia("(min-width: 1180px)").addEventListener("change", function (m) {
      if (m.matches) setOpen(false);
    });
  }

  /* ---------- 3. Enlace activo del menú según la sección visible ---------- */
  function initActiveNav() {
    var links = Array.prototype.slice.call(document.querySelectorAll(".nav-list a[href^='#']"));
    if (!links.length || !("IntersectionObserver" in window)) return;
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        links.forEach(function (a) { a.removeAttribute("aria-current"); });
        byId[entry.target.id].setAttribute("aria-current", "true");
      });
    }, { rootMargin: "-45% 0px -50% 0px" });

    Object.keys(byId).forEach(function (id) {
      var section = document.getElementById(id);
      if (section) observer.observe(section);
    });
  }

  /* ---------- 4. Aparición suave al hacer scroll ---------- */
  function initReveal() {
    var items = document.querySelectorAll("[data-reveal]");
    if (!("IntersectionObserver" in window)) {
      items.forEach(function (el) { el.classList.add("is-in"); });
      return;
    }
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-in");
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    items.forEach(function (el) { observer.observe(el); });
  }

  /* ---------- 5. Opiniones reales desde config.js ---------- */
  function initTestimonials() {
    var section = document.getElementById("opiniones");
    var list = document.getElementById("testimonials-list");
    if (!section || !list) return;

    /* La sección está oculta en el HTML: solo se muestra cuando hay opiniones reales */
    var data = Array.isArray(cfg.TESTIMONIALS) ? cfg.TESTIMONIALS : [];
    if (cfg.SHOW_TESTIMONIALS === false || !data.length) return;
    section.hidden = false;

    list.textContent = "";
    data.forEach(function (item) {
      var stars = Math.max(1, Math.min(5, Number(item.stars) || 5));
      var figure = document.createElement("figure");
      figure.className = "testimonial";

      var rating = document.createElement("p");
      rating.className = "stars";
      rating.setAttribute("role", "img");
      rating.setAttribute("aria-label", "Valoración: " + stars + " de 5 estrellas");
      rating.textContent = "★★★★★".slice(0, stars);

      var quote = document.createElement("blockquote");
      var text = document.createElement("p");
      text.textContent = "“" + String(item.text || "") + "”";
      quote.appendChild(text);

      var name = document.createElement("figcaption");
      name.textContent = String(item.name || "");

      figure.appendChild(rating);
      figure.appendChild(quote);
      figure.appendChild(name);
      list.appendChild(figure);
    });
  }

  /* ---------- 6. Formulario de presupuesto ---------- */
  var MESSAGES = {
    nombre: "Escribe tu nombre.",
    telefono: "Escribe un teléfono de contacto.",
    email: "Escribe un email válido, por ejemplo nombre@correo.com.",
    tipo_servicio: "Selecciona el tipo de servicio.",
    frecuencia: "Selecciona la frecuencia.",
    zona: "Indica el municipio o la zona.",
    privacidad: "Debes aceptar la política de privacidad y el aviso legal para enviar la solicitud."
  };

  function initForm() {
    var form = document.getElementById("quote-form");
    if (!form) return;
    var status = document.getElementById("form-status");
    var button = form.querySelector('button[type="submit"]');

    /* El texto bajo el botón explica qué pasa al enviar, según cómo esté configurado el envío */
    var note = document.getElementById("form-note");
    if (note && !cfg.FORM_ENDPOINT) {
      note.textContent = "Al pulsar el botón se abrirá tu correo con la solicitud ya escrita: solo tendrás que enviarla.";
    }

    function setError(field, message) {
      var wrap = field.closest(".field");
      var id = field.id + "-error";
      var error = document.getElementById(id);
      if (message) {
        if (!error) {
          error = document.createElement("p");
          error.className = "field-error";
          error.id = id;
          wrap.appendChild(error);
        }
        error.textContent = message;
        field.setAttribute("aria-invalid", "true");
        field.setAttribute("aria-describedby", id);
      } else {
        if (error) error.remove();
        field.removeAttribute("aria-invalid");
        field.removeAttribute("aria-describedby");
      }
    }

    function validate(field) {
      if (!field.willValidate) return true;
      var ok = field.checkValidity();
      setError(field, ok ? "" : (MESSAGES[field.name] || "Revisa este campo."));
      return ok;
    }

    form.addEventListener("input", function (e) {
      if (e.target.getAttribute("aria-invalid") === "true") validate(e.target);
    });
    form.addEventListener("change", function (e) {
      if (e.target.getAttribute("aria-invalid") === "true") validate(e.target);
    });

    function showStatus(html, isError) {
      status.innerHTML = html;
      status.classList.toggle("is-error", !!isError);
      status.hidden = false;
    }

    function collect() {
      var f = form.elements;
      return {
        nombre: f.nombre.value.trim(),
        telefono: f.telefono.value.trim(),
        email: f.email.value.trim(),
        tipo_servicio: f.tipo_servicio.value,
        zona: f.zona.value.trim(),
        frecuencia: f.frecuencia.value,
        mensaje: f.mensaje.value.trim()
      };
    }

    var emailLink = '<a href="mailto:' + cfg.EMAIL + '">' + cfg.EMAIL + "</a>";

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      status.hidden = true;

      var fields = Array.prototype.slice.call(form.querySelectorAll("input, select, textarea"));
      var invalid = fields.filter(function (field) { return !validate(field); });
      if (invalid.length) {
        invalid[0].focus();
        return;
      }
      if (form.elements.web.value) return; /* campo trampa relleno: envío automático */

      var data = collect();

      /* A) Servicio de formularios configurado en config.js */
      if (cfg.FORM_ENDPOINT) {
        button.disabled = true;
        /* Lo que llega al correo de SA NETA: los campos con su nombre y, para el servicio de envío,
           el asunto del mensaje y el formato en tabla. */
        var payload = {
          "Nombre": data.nombre,
          "Teléfono": data.telefono,
          "email": data.email,
          "Tipo de servicio": data.tipo_servicio,
          "Zona": data.zona,
          "Frecuencia": data.frecuencia,
          "Mensaje": data.mensaje || "(sin mensaje)",
          "_subject": "Solicitud de presupuesto · " + data.tipo_servicio + " · " + data.zona,
          "_template": "table",
          "_captcha": "false"
        };
        fetch(cfg.FORM_ENDPOINT, {
          method: "POST",
          headers: { "Content-Type": "application/json", "Accept": "application/json" },
          body: JSON.stringify(payload)
        }).then(function (response) {
          if (!response.ok) throw new Error("HTTP " + response.status);
          return response.json().catch(function () { return {}; });
        }).then(function (result) {
          /* Algunos servicios responden 200 aunque no hayan enviado nada (por ejemplo, antes de activar el correo) */
          if (result && String(result.success) === "false") throw new Error(result.message || "no enviado");
          form.reset();
          var thanks = document.getElementById("form-thanks");
          if (thanks) {
            form.hidden = true;
            thanks.hidden = false;
            thanks.focus();
            thanks.scrollIntoView({ block: "center" });
          } else {
            showStatus("Hemos recibido tu solicitud. Te responderemos lo antes posible.");
          }
        }).catch(function () {
          showStatus("No hemos podido enviar la solicitud. Inténtalo de nuevo o escríbenos a " + emailLink + ".", true);
        }).then(function () {
          button.disabled = false;
        });
        return;
      }

      /* B) Sin servicio configurado: se abre el correo del visitante con la solicitud redactada */
      var subject = "Solicitud de presupuesto · " + data.tipo_servicio + " · " + data.zona;
      var body = [
        "Nombre: " + data.nombre,
        "Teléfono: " + data.telefono,
        "Email: " + data.email,
        "Tipo de servicio: " + data.tipo_servicio,
        "Zona: " + data.zona,
        "Frecuencia: " + data.frecuencia,
        "",
        "Mensaje:",
        data.mensaje || "(sin mensaje)"
      ].join("\n");

      window.location.href = "mailto:" + cfg.EMAIL +
        "?subject=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(body);

      showStatus("Tu solicitud está preparada en tu aplicación de correo: solo falta pulsar <strong>Enviar</strong>. " +
        "Si no se ha abierto, escríbenos a " + emailLink + ".");
    });
  }

  /* ---------- 7. Galería: oculta hasta que haya fotografías reales (SHOW_GALLERY en config.js) ---------- */
  function initGallery() {
    var gallery = document.getElementById("galeria");
    if (gallery && cfg.SHOW_GALLERY === true) gallery.hidden = false;
  }

  /* ---------- 8. Datos estructurados: se completan con la web y el teléfono cuando están definidos ---------- */
  function initStructuredData() {
    var node = document.getElementById("ld-negocio");
    if (!node) return;
    try {
      var data = JSON.parse(node.textContent);
      if (!isPending(cfg.SITE_URL)) {
        var base = cfg.SITE_URL.replace(/\/+$/, "");
        data.url = base + "/";
        data.logo = base + "/assets/logo-oficial.png";
        data.image = base + "/assets/og-image.jpg";
      }
      if (!isPending(cfg.PHONE)) {
        data.telephone = (cfg.PHONE.trim().charAt(0) === "+" ? "+" : "") + digits(cfg.PHONE);
      }
      node.textContent = JSON.stringify(data);
    } catch (e) { /* si algo falla se queda el bloque original, que ya es válido */ }
  }

  /* ---------- 9. Aviso legal y de cookies: se muestra hasta que el visitante pulsa Aceptar ---------- */
  function initNotice() {
    var KEY = "saneta-aviso-aceptado";
    try {
      if (window.localStorage.getItem(KEY) === "1") return;
    } catch (e) { /* sin almacenamiento: se muestra el aviso en cada visita */ }

    var box = document.createElement("section");
    box.className = "notice";
    box.setAttribute("aria-label", "Aviso legal y de cookies");
    box.innerHTML =
      '<p>Esta web no utiliza cookies de seguimiento ni de publicidad. Al aceptar confirmas que has leído el ' +
      '<a href="aviso-legal.html">aviso legal</a>, la <a href="politica-privacidad.html">política de privacidad</a> y la ' +
      '<a href="politica-cookies.html">política de cookies</a>.</p>' +
      '<button class="btn btn-primary btn-small" type="button">Aceptar</button>';
    document.body.appendChild(box);

    box.querySelector("button").addEventListener("click", function () {
      try { window.localStorage.setItem(KEY, "1"); } catch (e) { /* no pasa nada */ }
      box.remove();
    });
  }

  applyConfig();
  initStructuredData();
  initGallery();
  initNotice();
  initHeader();
  initActiveNav();
  initReveal();
  initTestimonials();
  initForm();
})();
