// static/store/scripts/carousel.js
document.addEventListener("DOMContentLoaded", function () {

  /****************************************************
   * 1. Выпадающее меню в сайдбаре
   ****************************************************/
  document.querySelectorAll(".dropdown").forEach((dropdown) => {
    const arrow  = dropdown.querySelector(".sidebar-arrow");
    const anchor = dropdown.querySelector("a");
    const toggle = (e) => { e.preventDefault(); dropdown.classList.toggle("active"); };
    if (arrow)  arrow.addEventListener("click", toggle);
    if (anchor) anchor.addEventListener("click", toggle);
  });

  /****************************************************
   * 2. Карусель + swatch‑переключение (без перехода)
   ****************************************************/
  document.querySelectorAll(".product-card").forEach((card) => {
    const carousel = card.querySelector(".carousel-images");
    let images      = Array.from(carousel.querySelectorAll("img"));
    const left      = card.querySelector(".arrow-left");
    const right     = card.querySelector(".arrow-right");
    const dots      = card.querySelector(".dots");

    let idx = 0;
    const buildDots = () => {
      dots.innerHTML = "";
      images.forEach((_, i) => {
        const dot = document.createElement("span");
        dot.className = "dot";
        dot.addEventListener("click", (e) => {
          e.stopPropagation();
          idx = i;
          update();
        });
        dots.appendChild(dot);
      });
    };

    const update = () => {
      const w = carousel.offsetWidth;
      carousel.style.transform = `translateX(-${idx * w}px)`;
      dots.querySelectorAll(".dot").forEach((d, i) => {
        d.classList.toggle("active", i === idx);
      });
      if (left && right) {
        const show = images.length > 1;
        left.style.display  = show ? "block" : "none";
        right.style.display = show ? "block" : "none";
      }
    };

    if (left) {
      left.addEventListener("click", (e) => {
        e.stopPropagation();
        idx = (idx - 1 + images.length) % images.length;
        update();
      });
    }
    if (right) {
      right.addEventListener("click", (e) => {
        e.stopPropagation();
        idx = (idx + 1) % images.length;
        update();
      });
    }

    // клик по swatch — меняем картинки только в этой карточке
    card.querySelectorAll(".color-swatch").forEach((sw) => {
      sw.addEventListener("click", (e) => {
        e.stopPropagation();
        if (sw.dataset.empty) return;
        const newUrls = [];
        if (sw.dataset.front) newUrls.push(sw.dataset.front);
        if (sw.dataset.back)  newUrls.push(sw.dataset.back);
        if (!newUrls.length) return;

        carousel.innerHTML = "";
        newUrls.forEach((url) => {
          const img = document.createElement("img");
          img.src = url;
          carousel.appendChild(img);
        });
        images = Array.from(carousel.querySelectorAll("img"));
        idx = 0;
        buildDots();
        update();
      });
    });

    // клик по карточке — переходим на detail, если не по swatch
    card.addEventListener("click", (e) => {
      if (!e.target.classList.contains("color-swatch")) {
        const url = card.dataset.productUrl;
        if (url) window.location.href = url;
      }
    });

    buildDots();
    update();
  });

  /****************************************************
   * 3. Детальная страница: миниатюры и табы (unchanged)
   ****************************************************/
  const mainImage  = document.getElementById("mainImage");
  const thumbs     = document.querySelectorAll(".thumbnail");
  thumbs.forEach((thumb) => {
    thumb.addEventListener("click", () => {
      if (!mainImage) return;
      [mainImage.src, thumb.src] = [thumb.src, mainImage.src];
    });
  });

  const tabButtons = document.querySelectorAll(".tab-button");
  const tabPanels  = document.querySelectorAll(".tab-panel");
  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabButtons.forEach((b) => b.classList.toggle("active", b === btn));
      const target = btn.dataset.tab;
      tabPanels.forEach((panel) => {
        panel.classList.toggle("hidden", panel.id !== target);
      });
    });
  });

});