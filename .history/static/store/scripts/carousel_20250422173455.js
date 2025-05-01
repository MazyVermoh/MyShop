// static/store/scripts/carousel.js
document.addEventListener("DOMContentLoaded", function () {

  /****************************************************
   * 1. Выпадающее меню в сайдбаре
   ****************************************************/
  document.querySelectorAll(".dropdown").forEach((dropdown) => {
    const arrow  = dropdown.querySelector(".sidebar-arrow");
    const anchor = dropdown.querySelector("a");
    const toggle = (e) => { e.preventDefault(); dropdown.classList.toggle("active"); };
    arrow?.addEventListener("click", toggle);
    anchor?.addEventListener("click", toggle);
  });

  /****************************************************
   * 2. Карусель + swatch‑ и size‑переключение на главной
   ****************************************************/
  document.querySelectorAll(".product-card").forEach((card) => {
    const carousel   = card.querySelector(".carousel-images");
    let images        = Array.from(carousel.querySelectorAll("img"));
    const left        = card.querySelector(".arrow-left");
    const right       = card.querySelector(".arrow-right");
    const dots        = card.querySelector(".dots");
    const swatches    = card.querySelectorAll(".color-swatch");
    const sizeOptions = card.querySelectorAll(".size-option");

    let idx = 0;
    function buildDots() {
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
    }
    function update() {
      const w = carousel.offsetWidth;
      carousel.style.transform = `translateX(-${idx * w}px)`;
      dots.querySelectorAll(".dot").forEach((d,i) => {
        d.classList.toggle("active", i === idx);
      });
      if (left && right) {
        const show = images.length > 1;
        left.style.display  = show ? "block" : "none";
        right.style.display = show ? "block" : "none";
      }
    }
    left?.addEventListener("click", (e) => { e.stopPropagation(); idx=(idx-1+images.length)%images.length; update(); });
    right?.addEventListener("click", (e) => { e.stopPropagation(); idx=(idx+1)%images.length; update(); });

    // Цветовые swatch’и
    swatches.forEach((sw) => {
      sw.addEventListener("click", (e) => {
        e.stopPropagation();
        if (sw.dataset.empty) return;
        // Запоминаем выбор цвета
        card.dataset.selectedColor = sw.dataset.colorId;

        // Меняем карусель
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

    // Size‑переключение
    sizeOptions.forEach((sz) => {
      sz.addEventListener("click", (e) => {
        e.stopPropagation();
        // Запоминаем выбор размера
        card.dataset.selectedSize = sz.dataset.size;
        // Визуально выделяем
        sizeOptions.forEach(s => s.classList.toggle("active", s === sz));
      });
    });

    // Клик по карточке → переход на detail с параметрами
    card.addEventListener("click", (e) => {
      if (e.target.classList.contains("color-swatch") ||
          e.target.classList.contains("size-option")) return;
      let url = card.dataset.productUrl;
      const col = card.dataset.selectedColor;
      const sz  = card.dataset.selectedSize;
      const params = new URLSearchParams();
      if (col) params.set("color", col);
      if (sz)  params.set("size", sz);
      const query = params.toString();
      if (query) url += `?${query}`;
      window.location.href = url;
    });

    buildDots();
    update();
  });

  /****************************************************
   * 3. Страница товара: переключение миниатюр и swatch/size
   ****************************************************/
  const mainImage = document.getElementById("mainImage");
  const thumbs    = document.querySelector(".thumbnail-container");

  // миниатюры
  document.querySelectorAll(".thumbnail").forEach((thumb) => {
    thumb.addEventListener("click", () => {
      if (!mainImage) return;
      [mainImage.src, thumb.src] = [thumb.src, mainImage.src];
    });
  });

  // swatch на детальной
  document.querySelectorAll(".detail-swatch").forEach((sw) => {
    sw.addEventListener("click", (e) => {
      e.preventDefault();
      if (sw.dataset.empty) return;
      if (sw.dataset.front) mainImage.src = sw.dataset.front;
      thumbs.innerHTML = "";
      if (sw.dataset.back) {
        const img = document.createElement("img");
        img.className = "thumbnail";
        img.src       = sw.dataset.back;
        thumbs.appendChild(img);
      }
      document.querySelectorAll(".detail-swatch").forEach(s => {
        s.dataset.active = (s === sw) ? "1" : "";
      });
    });
  });

  // size‑select на детальной
  document.querySelectorAll(".custom-select select").forEach((select) => {
    select.addEventListener("change", () => {
      // здесь можно сохранить выбранный размер или отправить форму
      // например: console.log("Selected size:", select.value);
    });
  });

  /****************************************************
   * 4. Вкладки на странице товара
   ****************************************************/
  document.querySelectorAll(".tab-button").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-button").forEach(b =>
        b.classList.toggle("active", b === btn)
      );
      const target = btn.dataset.tab;
      document.querySelectorAll(".tab-panel").forEach(panel =>
        panel.classList.toggle("hidden", panel.id !== target)
      );
    });
  });

});