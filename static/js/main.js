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

  const isStaticMode = !!document.querySelector('meta[name="turon-static-mode"]');

  // CTA bosilishlarini qayd etish
  const csrfMeta = document.querySelector('meta[name="csrf-token"]');
  const csrfToken = csrfMeta ? csrfMeta.getAttribute("content") : "";
  document.querySelectorAll("[data-track-cta]").forEach(function (el) {
    el.addEventListener("click", function () {
      if (isStaticMode) return;
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
  // GitHub Pages statik rejimda formalarni xatosiz yo'naltirish va izohlarni darhol chiqarish
  if (isStaticMode) {
    const reviewsStorageKey = "turon_live_reviews_v1";
    const reviewArticlesContainer = document.querySelector(".grid.grid-2 > div:first-child");

    function renderSavedStaticReviews() {
      if (!reviewArticlesContainer || !window.location.pathname.includes("/fikrlar")) return;
      let saved = [];
      try {
        saved = JSON.parse(localStorage.getItem(reviewsStorageKey) || "[]");
      } catch (err) {
        saved = [];
      }
      document.querySelectorAll(".user-live-review-card").forEach(function (el) { el.remove(); });
      const filterPills = reviewArticlesContainer.querySelector(".filter-pills");
      saved.slice().reverse().forEach(function (item) {
        const card = document.createElement("article");
        card.className = "card user-live-review-card";
        card.style.marginBottom = "16px";
        let starsHtml = "";
        for (let i = 1; i <= 5; i++) {
          starsHtml += i <= item.rating ? "&#9733;" : "&#9734;";
        }
        const safeComment = document.createElement("p");
        safeComment.style.marginTop = "0";
        safeComment.textContent = item.comment;
        const safeAuthor = document.createElement("strong");
        safeAuthor.textContent = item.author;
        card.innerHTML =
          '<div style="display:flex; justify-content:space-between; align-items:center; gap:8px; margin-bottom:8px;">' +
          '<span class="stars" aria-label="' + item.rating + ' dan 5 baho">' + starsHtml + "</span>" +
          '<div><small style="color:var(--muted);">' + item.date + "</small></div>" +
          "</div>";
        card.appendChild(safeComment);
        const metaDiv = document.createElement("div");
        metaDiv.style.fontSize = "0.88rem";
        metaDiv.style.color = "var(--muted)";
        metaDiv.appendChild(safeAuthor);
        metaDiv.appendChild(document.createTextNode(" • " + (item.branch || "Turon Odob-Ilm — Furqat filiali")));
        card.appendChild(metaDiv);
        if (filterPills && filterPills.nextSibling) {
          reviewArticlesContainer.insertBefore(card, filterPills.nextSibling);
        } else {
          reviewArticlesContainer.appendChild(card);
        }
      });
    }

    renderSavedStaticReviews();

    document.querySelectorAll('form[method="post"]').forEach(function (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        const commentField = form.querySelector('textarea[name="comment"]');
        const authorField = form.querySelector('input[name="author_name"]');
        if (commentField && authorField) {
          const authorVal = (authorField.value || "").trim() || "Ota-ona";
          const displayField = form.querySelector('input[name="display_name"]');
          const displayVal = (displayField && displayField.value ? displayField.value.trim() : "") || authorVal;
          const commentVal = (commentField.value || "").trim();
          const ratingChecked = form.querySelector('input[name="rating"]:checked');
          const ratingVal = ratingChecked ? parseInt(ratingChecked.value, 10) || 5 : 5;
          const branchSelect = form.querySelector('select[name="branch"]');
          const branchText = branchSelect && branchSelect.options[branchSelect.selectedIndex]
            ? branchSelect.options[branchSelect.selectedIndex].text
            : "Turon Odob-Ilm — Furqat filiali";

          if (commentVal.length < 3) {
            let errBox = form.querySelector(".static-form-notice");
            if (!errBox) {
              errBox = document.createElement("div");
              errBox.className = "alert alert-info static-form-notice";
              errBox.style.marginTop = "14px";
              form.appendChild(errBox);
            }
            errBox.textContent = "Iltimos, fikr matnini kiriting.";
            return;
          }

          let saved = [];
          try {
            saved = JSON.parse(localStorage.getItem(reviewsStorageKey) || "[]");
          } catch (err) {
            saved = [];
          }
          const now = new Date();
          const dd = String(now.getDate()).padStart(2, "0");
          const mm = String(now.getMonth() + 1).padStart(2, "0");
          const yyyy = now.getFullYear();
          saved.push({
            author: displayVal,
            comment: commentVal,
            rating: ratingVal,
            branch: branchText,
            date: dd + "." + mm + "." + yyyy
          });
          localStorage.setItem(reviewsStorageKey, JSON.stringify(saved));
          renderSavedStaticReviews();
          form.reset();

          let notice = form.querySelector(".static-form-notice");
          if (!notice) {
            notice = document.createElement("div");
            notice.className = "alert alert-success static-form-notice";
            notice.style.marginTop = "14px";
            form.appendChild(notice);
          }
          notice.className = "alert alert-success static-form-notice";
          notice.innerHTML = "<strong>Fikringiz uchun rahmat!</strong> Izohingiz muvaffaqiyatli qabul qilindi va ro‘yxatga qo‘shildi.";
          return;
        }

        let notice = form.querySelector(".static-form-notice");
        if (!notice) {
          notice = document.createElement("div");
          notice.className = "alert alert-success static-form-notice";
          notice.style.marginTop = "14px";
          form.appendChild(notice);
        }
        notice.innerHTML =
          "<strong>Murojaatingiz qabul qilindi!</strong> Tezkor bog‘lanish uchun telefon yoki Telegram orqali ham murojaat qilishingiz mumkin:" +
          '<div class="btn-group-wrap" style="margin-top:10px;">' +
          '<a href="tel:+998558085575" class="btn btn-gold btn-sm">Qo‘ng‘iroq: +998 55 808 55 75</a>' +
          '<a href="https://t.me/turonodobilm" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm">Telegram (@turonodobilm)</a>' +
          "</div>";
      });
    });
  }
})();
