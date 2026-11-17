(function () {
  "use strict";

  // Mobil menyu
  const navToggle = document.getElementById("navToggle");
  const siteNav = document.getElementById("siteNav");
  if (navToggle && siteNav) {
    navToggle.addEventListener("click", function () {
      const expanded = siteNav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", expanded ? "true" : "false");
    });
  }

  // Maxfiylik / analitika cookie xabarnomasi
  const banner = document.getElementById("cookieBanner");
  const acceptBtn = document.getElementById("cookieAcceptBtn");
  const storageKey = "turon_privacy_notice_ack_v1";
  if (banner && !localStorage.getItem(storageKey)) {
    banner.classList.add("is-visible");
  }
  if (acceptBtn && banner) {
    acceptBtn.addEventListener("click", function () {
      localStorage.setItem(storageKey, "1");
      banner.classList.remove("is-visible");
    });
  }

  // CTA bosilishlarini qayd etish
  const csrfMeta = document.querySelector('meta[name="csrf-token"]');
  const csrfToken = csrfMeta ? csrfMeta.getAttribute("content") : "";
  document.querySelectorAll("[data-track-cta]").forEach(function (el) {
    el.addEventListener("click", function () {
      const label = el.getAttribute("data-track-cta");
      const branchId = el.getAttribute("data-branch-id") || "";
      if (!label || !csrfToken) return;
      fetch("/api/track-cta/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": csrfToken
        },
        body: JSON.stringify({
          cta_label: label,
          branch_id: branchId || null,
          page_path: window.location.pathname
        }),
        keepalive: true
      }).catch(function () {});
    });
  });

  // Galereya rasmini kattalashtirish (Lightbox)
  const lightbox = document.getElementById("galleryLightbox");
  const lightboxImg = document.getElementById("lightboxImg");
  const lightboxCaption = document.getElementById("lightboxCaption");
  const lightboxClose = document.getElementById("lightboxClose");

  document.querySelectorAll("[data-lightbox-src]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (!lightbox || !lightboxImg) return;
      lightboxImg.src = btn.getAttribute("data-lightbox-src");
      lightboxImg.alt = btn.getAttribute("data-lightbox-title") || "Maktab surati";
      if (lightboxCaption) {
        lightboxCaption.textContent = btn.getAttribute("data-lightbox-title") || "";
      }
      lightbox.classList.add("is-open");
    });
  });
  if (lightboxClose && lightbox) {
    lightboxClose.addEventListener("click", function () { lightbox.classList.remove("is-open"); });
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) lightbox.classList.remove("is-open");
    });
  }
})();
