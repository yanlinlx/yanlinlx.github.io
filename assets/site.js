/* Academic homepage — small progressive enhancements. */
(function () {
  "use strict";

  /* ---- theme toggle (remembers the choice) ---- */
  var toggle = document.querySelector(".theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var root = document.documentElement;
      var current = root.getAttribute("data-theme");
      if (!current) {
        var prefersDark =
          window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
        current = prefersDark ? "dark" : "light";
      }
      var next = current === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try {
        localStorage.setItem("theme", next);
      } catch (e) {
        /* private mode — ignore */
      }
    });
  }

  /* ---- click-to-load YouTube: no iframe until the visitor asks for it ---- */
  function loadVideo(el) {
    var id = el.getAttribute("data-youtube");
    if (!id || el.getAttribute("data-loaded")) return;
    el.setAttribute("data-loaded", "1");
    var iframe = document.createElement("iframe");
    iframe.src =
      "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0&modestbranding=1";
    iframe.title = el.getAttribute("data-title") || "Video";
    iframe.allow =
      "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    iframe.allowFullscreen = true;
    el.innerHTML = "";
    el.appendChild(iframe);
  }

  Array.prototype.forEach.call(document.querySelectorAll(".video-embed"), function (el) {
    el.addEventListener("click", function () {
      loadVideo(el);
    });
    el.addEventListener("keydown", function (event) {
      if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        loadVideo(el);
      }
    });
  });
})();
