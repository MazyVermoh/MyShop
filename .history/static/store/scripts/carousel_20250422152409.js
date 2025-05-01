// static/store/scripts/carousel.js
document.addEventListener("DOMContentLoaded", function () {

  /****************************************************
   * 1. Выпадающее меню в сайдбаре
   ****************************************************/
  const dropdowns = document.querySelectorAll(".dropdown");
  dropdowns.forEach((dropdown) => {
    const sidebarArrow   = dropdown.querySelector(".sidebar-arrow");
    const dropdownAnchor = dropdown.querySelector("a");

    function toggleDropdown(e) {
      e.preventDefault();
      dropdown.classList.toggle("active");
    }

    if (sidebarArrow)   sidebarArrow.addEventListener("click", toggleDropdown);
    if (dropdownAnchor) dropdownAnchor.addEventListener("click", toggleDropdown);
  });

  /****************************************************
   * 2. Карусель для карточек товаров + swatch‑переключение
   ****************************************************/
  const productCards = document.querySelectorAll(".product-card");

  productCards.forEach((card) => {
    const carouselContainer = card.querySelector(".carousel-images");
    const images            = Array.from(card.querySelectorAll(".carousel-images img"));
    const arrowLeft         = card.querySelector(".arrow-left");
    const arrowRight        = card.querySelector(".arrow-right");
    const dotsContainer     = card.querySelector(".dots");
    const swatches          = card.querySelectorAll(".color-swatch");

    if (!carouselContainer || images.length === 0) return;

    let currentIndex = 0;

    /* — построить точки‑индикаторы — */
    function buildDots() {
      dotsContainer.innerHTML = "";
      images.forEach((_, i) => {
        const dot = document.createElement("span");
        dot.classList.add("dot");
        dot.addEventListener("click", (e) => {
          e.stopPropagation();
          e.preventDefault();
          currentIndex = i;
          updateCarousel();
        });
        dotsContainer.appendChild(dot);
      });
    }

    /* — обновить позицию слайда и активность точек/стрелок — */
    function updateCarousel() {
      const slideWidth = carouselContainer.offsetWidth;
      carouselContainer.style.transform =
        `translateX(-${currentIndex * slideWidth}px)`;

      dotsContainer.querySelectorAll(".dot").forEach((d, i) => {
        d.classList.toggle("active", i === currentIndex);
      });

      if (arrowLeft && arrowRight) {
        const show = images.length > 1;
        arrowLeft.style.display  = show ? "block" : "none";
        arrowRight.style.display = show ? "block" : "none";
      }
    }

    /* — стрелки — */
    if (arrowLeft) {
      arrowLeft.addEventListener("click", (e) => {
        e.stopPropagation();
        e.preventDefault();
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        updateCarousel();
      });
    }
    if (arrowRight) {
      arrowRight.addEventListener("click", (e) => {
        e.stopPropagation();
        e.preventDefault();
        currentIndex = (currentIndex + 1) % images.length;
        updateCarousel();
      });
    }

    /* — клик по swatch внутри КАРТОЧКИ — переключаем картинки (front/back) — */
    swatches.forEach((sw) => {
      sw.addEventListener("click", (e) => {
        /* здесь только логика «сменить картинку внутри карточки»;
           фильтр по цвету реализован ниже, глобально */
        e.stopPropagation();
        e.preventDefault();

        const front = sw.dataset.front;
        const back  = sw.dataset.back;
        const newUrls = [];
        if (front) newUrls.push(front);
        if (back)  newUrls.push(back);

        if (!newUrls.length) return;

        carouselContainer.innerHTML = "";
        newUrls.forEach((src) => {
          const img = document.createElement("img");
          img.src = src;
          img.alt = "";
          carouselContainer.appendChild(img);
        });

        /* обновляем локальный массив изображений */
        images.length = 0;
        carouselContainer.querySelectorAll("img").forEach((img) => images.push(img));

        currentIndex = 0;
        buildDots();
        updateCarousel();
      });
    });

    /* — инициализация — */
    buildDots();
    updateCarousel();
  });

  /****************************************************
   * 2‑bis.  Клик по карточке → переход на страницу товара
   *        (но только если клик был НЕ по swatch)
   ****************************************************/
  productCards.forEach((card) => {
    const url = card.dataset.productUrl;
    if (!url) return;

    card.addEventListener("click", (e) => {
      if (!e.target.classList.contains("color-swatch")) {
        window.location.href = url;
      }
    });
  });

  /****************************************************
   * 2‑ter.  Клик по swatch вне зависимости от карусели
   *        → фильтр товаров (?color=<id>)
   ****************************************************/
  const allSwatches = document.querySelectorAll(".color-swatch");
  allSwatches.forEach((sw) => {
    sw.addEventListener("click", (e) => {
      /* swatch внутри карточки уже вызвал e.stopPropagation()
         из блока 2, поэтому сюда мы попадаем только для «глобального» действия
         (фильтрации). */
      if (sw.dataset.empty === "1") return;       // нет фото -> ничего не делаем
      const url = sw.dataset.filterUrl;
      if (url) window.location.search = url;      // ?color=<id>
    });
  });

  /****************************************************
   * 3. Детальная страница товара: переключение миниатюр
   ****************************************************/
  const mainImage   = document.getElementById("mainImage");
  const thumbnails  = document.querySelectorAll(".thumbnail");
  thumbnails.forEach((thumb) => {
    thumb.addEventListener("click", () => {
      if (!mainImage) return;
      [mainImage.src, thumb.src] = [thumb.src, mainImage.src];
    });
  });

  /****************************************************
   * 4. Вкладки (Описание / Доп. информация)
   ****************************************************/
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabPanels  = document.querySelectorAll(".tab-panel");
  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabButtons.forEach((b) => b.classList.toggle("active", b === btn));

      const targetId = btn.dataset.tab;
      tabPanels.forEach((panel) =>
        panel.classList.toggle("hidden", panel.id !== targetId)
      );
    });
  });
});