/* global document, window */
document.addEventListener("DOMContentLoaded", () => {

  /******************** 1. sidebar dropdowns (как было) */
  document.querySelectorAll(".dropdown").forEach(dd => {
    const arrow = dd.querySelector(".sidebar-arrow");
    const anchor = dd.querySelector("a");
    [arrow, anchor].forEach(el => {
      if (el) el.addEventListener("click", e => { e.preventDefault(); dd.classList.toggle("active"); });
    });
  });

  /******************** 2. карточки‑товары на главной */
  document.querySelectorAll(".product-card").forEach(card => {

    /* ---------------- 2.1 карусель */
    const track   = card.querySelector(".carousel-images");
    const slides  = card.querySelectorAll(".carousel-images img");
    const leftAr  = card.querySelector(".arrow-left");
    const rightAr = card.querySelector(".arrow-right");
    const dotsBox = card.querySelector(".dots");
    if (!track || slides.length === 0) return;

    let idx = 0;
    buildDots();
    update();

    function buildDots() {
      dotsBox.innerHTML = "";
      slides.forEach((_, i) => {
        const d = document.createElement("span");
        d.className = "dot";
        d.addEventListener("click", e => { e.stopPropagation(); e.preventDefault(); idx = i; update(); });
        dotsBox.appendChild(d);
      });
    }

    function update() {
      track.style.transform = `translateX(-${idx * track.offsetWidth}px)`;
      dotsBox.querySelectorAll(".dot").forEach((d,i) => d.classList.toggle("active", i === idx));
      const arrowsVis = slides.length > 1 ? "block" : "none";
      if (leftAr)  leftAr.style.display  = arrowsVis;
      if (rightAr) rightAr.style.display = arrowsVis;
    }

    leftAr  && leftAr .addEventListener("click", e => { e.stopPropagation(); e.preventDefault(); idx = (idx-1+slides.length)%slides.length; update(); });
    rightAr && rightAr.addEventListener("click", e => { e.stopPropagation(); e.preventDefault(); idx = (idx+1)%slides.length; update(); });

    /* ---------------- 2.2  клик по РАЗМЕРУ → переход + size‑параметр */
    card.querySelectorAll(".size-option").forEach(sizeEl => {
      sizeEl.addEventListener("click", e => {
        e.preventDefault(); e.stopPropagation();
        const sz = sizeEl.textContent.trim();
        const link = card.closest("a.product-card");
        if (link) window.location.href = `${link.href}?size=${encodeURIComponent(sz)}`;
      });
    });

    /* ---------------- 2.3  клик по ЦВЕТУ → подменяем картинки */
    card.querySelectorAll(".color-swatch").forEach(sw => {
      sw.addEventListener("click", e => {
        e.preventDefault(); e.stopPropagation();
        const f = sw.dataset.front, b = sw.dataset.back;
        if (f) slides[0].src = f;
        if (b) {
          if (slides[1]) slides[1].src = b;
          else {                                     // если второго слайда не было
            const img = document.createElement("img");
            img.src = b;
            track.appendChild(img);
            buildDots();
          }
        }
        idx = 0; update();
      });
    });

  }); //‑‑ end .product‑card loop



  /******************** 3. внутри страницы товара – автовыбор размера */
  const params = new URLSearchParams(window.location.search);
  const preset = params.get("size");
  if (preset) {
    const sel = document.getElementById("sizeSelect");
    if (sel) sel.value = preset;
  }

  /******************** 4. галерея миниатюр на детальной странице */
  const mainImg = document.getElementById("mainImage");
  document.querySelectorAll(".thumbnail").forEach(thumb => {
    thumb.addEventListener("click", () => {
      if (!mainImg) return;
      [mainImg.src, thumb.src] = [thumb.src, mainImg.src];
    });
  });
});