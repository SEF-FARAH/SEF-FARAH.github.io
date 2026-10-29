// Menu mobile : ouverture/fermeture du menu de navigation
(function () {
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("nav");
  if (!toggle || !nav) return;

  function setOpen(open) {
    nav.classList.toggle("nav--open", open);
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  }

  toggle.addEventListener("click", function () {
    setOpen(toggle.getAttribute("aria-expanded") !== "true");
  });

  nav.addEventListener("click", function (e) {
    if (e.target.closest("a")) setOpen(false);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setOpen(false);
  });
})();
