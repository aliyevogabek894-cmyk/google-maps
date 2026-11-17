(function () {
  "use strict";

  // Mobil menyu
  const navToggle = document.getElementById("navToggle");
  const siteNav = document.getElementById("siteNav");
  if (navToggle && siteNav) {
    const labelEl = navToggle.querySelector(".nav-toggle-label");
    function setMenuState(open) {
      siteNav.classList.toggle("is-open", open);
      navToggle.classList.toggle("is-open", open);
      navToggle.setAttribute("aria-expanded", open ? "true" : "false");
      navToggle.setAttribute("aria-label", open ? "Menyuni yopish" : "Menyuni ochish");
      document.body.classList.toggle("nav-drawer-open", open);
      if (labelEl) {
        labelEl.textContent = open ? "Yopish" : "Menyu";
      }
    }
    navToggle.addEventListener("click", function () {
      setMenuState(!siteNav.classList.contains("is-open"));
    });
    siteNav.querySelectorAll("a").forEach(function (link) {
      link.addEventListener("click", function () { setMenuState(false); });
    });
    document.addEventListener("click", function (e) {
      if (siteNav.classList.contains("is-open") && !siteNav.contains(e.target) && !navToggle.contains(e.target)) {
        setMenuState(false);
      }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && siteNav.classList.contains("is-open")) {
        setMenuState(false);
      }
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth >= 1080 && siteNav.classList.contains("is-open")) {
        setMenuState(false);
      }
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
  const lightboxSource = document.getElementById("lightboxSource");
  const lightboxClose = document.getElementById("lightboxClose");

  document.querySelectorAll("[data-lightbox-src]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      if (!lightbox || !lightboxImg) return;
      lightboxImg.src = btn.getAttribute("data-lightbox-src");
      lightboxImg.alt = btn.getAttribute("data-lightbox-alt") || btn.getAttribute("data-lightbox-title") || "Maktab surati";
      if (lightboxCaption) {
        lightboxCaption.textContent = btn.getAttribute("data-lightbox-title") || "Maktab surati";
      }
      if (lightboxSource) {
        const srcUrl = btn.getAttribute("data-lightbox-source") || "";
        if (srcUrl) {
          lightboxSource.href = srcUrl;
          lightboxSource.style.display = "inline";
        } else {
          lightboxSource.style.display = "none";
        }
      }
      lightbox.classList.add("is-open");
    });
  });
  if (lightboxClose && lightbox) {
    lightboxClose.addEventListener("click", function () { lightbox.classList.remove("is-open"); });
    lightbox.addEventListener("click", function (e) {
      if (e.target === lightbox) lightbox.classList.remove("is-open");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && lightbox.classList.contains("is-open")) {
        lightbox.classList.remove("is-open");
      }
    });
  }

  // YouTube video facade (tezlik uchun bosilganda iframe yuklanadi)
  document.querySelectorAll("[data-youtube-embed]").forEach(function (box) {
    box.addEventListener("click", function () {
      const embedUrl = box.getAttribute("data-youtube-embed");
      const title = box.getAttribute("data-youtube-title") || "Turon Odob-Ilm video";
      if (!embedUrl || box.dataset.loaded === "1") return;
      box.dataset.loaded = "1";
      const iframe = document.createElement("iframe");
      iframe.className = "video-iframe";
      iframe.src = embedUrl + (embedUrl.includes("?") ? "&autoplay=1" : "?autoplay=1");
      iframe.title = title;
      iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
      iframe.allowFullscreen = true;
      box.innerHTML = "";
      box.appendChild(iframe);
    });
  });

  // Scroll reveal (prefers-reduced-motion hurmat qilinadi)
  const revealItems = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && revealItems.length) {
    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    revealItems.forEach(function (el) { observer.observe(el); });
  } else {
    revealItems.forEach(function (el) { el.classList.add("is-visible"); });
  }
})();
