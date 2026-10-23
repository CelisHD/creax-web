// Creax — menú móvil y formulario de cotización por WhatsApp.
(function () {
  "use strict";

  // Menú móvil
  var toggle = document.querySelector(".menu-toggle");
  var nav = document.getElementById("menu");
  if (toggle && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Cerrar menú" : "Abrir menú");
    };
    toggle.addEventListener("click", function () {
      setOpen(!nav.classList.contains("is-open"));
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setOpen(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setOpen(false);
    });
  }

  // Marca el enlace activo según la sección visible
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav a[href^="#"]:not(.btn)'));
  if ("IntersectionObserver" in window && links.length) {
    var byId = {};
    links.forEach(function (a) { byId[a.getAttribute("href").slice(1)] = a; });
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting || !byId[en.target.id]) return;
        links.forEach(function (a) { a.removeAttribute("aria-current"); });
        byId[en.target.id].setAttribute("aria-current", "page");
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    Object.keys(byId).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) obs.observe(el);
    });
  }

  // Formulario: arma el mensaje y lo abre en WhatsApp
  var form = document.getElementById("form-cotizar");
  if (form) {
    var error = document.getElementById("form-error");
    var done = document.getElementById("form-done");
    var link = document.getElementById("form-link");
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var v = function (name) { return (form.elements[name].value || "").trim(); };
      var emailBad = v("email") && !form.elements.email.checkValidity();
      if (!v("nombre") || !v("proyecto") || emailBad) {
        error.hidden = false;
        (!v("nombre") ? form.elements.nombre : !v("proyecto") ? form.elements.proyecto : form.elements.email).focus();
        return;
      }
      error.hidden = true;
      var lines = [
        "Hola, quiero cotizar un proyecto.",
        "",
        "Nombre: " + v("nombre"),
        v("empresa") ? "Empresa: " + v("empresa") : null,
        v("email") ? "Correo: " + v("email") : null,
        v("telefono") ? "Teléfono: " + v("telefono") : null,
        "",
        "Proyecto: " + v("proyecto")
      ].filter(function (l) { return l !== null; });
      var url = "https://wa.me/" + form.dataset.whatsapp + "?text=" + encodeURIComponent(lines.join("\n"));
      link.href = url;
      done.hidden = false;
      window.open(url, "_blank", "noopener");
      link.focus();
    });
  }
})();
