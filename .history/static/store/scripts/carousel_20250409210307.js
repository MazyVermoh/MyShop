document.addEventListener("DOMContentLoaded", function () {
  /****************************************************
   * 1. Выпадающее меню в сайдбаре (пример)
   ****************************************************/
  const dropdowns = document.querySelectorAll(".dropdown");
  dropdowns.forEach((dropdown) => {
    const sidebarArrow = dropdown.querySelector(".sidebar-arrow");
    const dropdownAnchor = dropdown.querySelector("a");

    if (sidebarArrow) {
      sidebarArrow.addEventListener("click", function (e) {
        e.preventDefault();
        dropdown.classList.toggle("active");
      });
    }
    if (dropdownAnchor) {
      dropdownAnchor.addEventListener("click", function (e) {
        e.preventDefault();
        dropdown.classList.toggle("active");
      });
    }
  });

  /****************************************************
   * 2. Карусель для карточек товаров
   ****************************************************/
  const productCards = document.querySelectorAll(".product-card");
  productCards.forEach((card) => {
    const carouselContainer = card.querySelector(".carousel-images");
    const images = carouselContainer ? carouselContainer.querySelectorAll("img") : [];
    const arrowLeft = card.querySelector(".arrow-left");
    const arrowRight = card.querySelector(".arrow-right");
    const dotsContainer = card.querySelector(".dots");

    // Если нет изображений, выходим
    if (!carouselContainer || images.length === 0) return;

    let currentIndex = 0;

    // Создаём «точки» (dots) на основе кол-ва изображений
    dotsContainer.innerHTML = "";
    images.forEach((_, i) => {
      const dot = document.createElement("span");
      dot.classList.add("dot");
      // Блокируем переход, если dots внутри ссылки
      dot.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        currentIndex = i;
        updateCarousel();
      });
      dotsContainer.appendChild(dot);
    });

    // Функция обновления положения карусели
    function updateCarousel() {
      const slideWidth = carouselContainer.offsetWidth;
      carouselContainer.style.transform = `translateX(-${currentIndex * slideWidth}px)`;

      // Активная точка
      const allDots = dotsContainer.querySelectorAll(".dot");
      allDots.forEach((d) => d.classList.remove("active"));
      if (allDots[currentIndex]) {
        allDots[currentIndex].classList.add("active");
      }

      // Скрываем стрелки, если только 1 изображение
      if (arrowLeft && arrowRight) {
        arrowLeft.style.display = images.length <= 1 ? "none" : "block";
        arrowRight.style.display = images.length <= 1 ? "none" : "block";
      }
    }

    // Инициализация
    updateCarousel();

    // Обработчики клика на стрелки (не ведут на детальную страницу, т.к. вне <a>)
    if (arrowLeft) {
      arrowLeft.addEventListener("click", (e) => {
        e.preventDefault();
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        updateCarousel();
      });
    }
    if (arrowRight) {
      arrowRight.addEventListener("click", (e) => {
        e.preventDefault();
        currentIndex = (currentIndex + 1) % images.length;
        updateCarousel();
      });
    }

    /****************************************************
     * 3. Смена цвета (color-swatch)
     ****************************************************/
    const colorSwatches = card.querySelectorAll(".color-swatch");
    colorSwatches.forEach((swatch) => {
      swatch.addEventListener("click", (e) => {
        // Блокируем переход, т.к. внутри <a>
        e.preventDefault();
        e.stopPropagation();
        const frontImage = swatch.getAttribute("data-front");
        const backImage = swatch.getAttribute("data-back");
        if (images[0]) images[0].src = frontImage;
        if (images[1]) images[1].src = backImage;

        currentIndex = 0;
        updateCarousel();
      });
    });

    /****************************************************
     * 4. Выбор размера (size-span)
     ****************************************************/
    const sizeSpans = card.querySelectorAll(".size-span");
    sizeSpans.forEach((sizeEl) => {
      sizeEl.addEventListener("click", (e) => {
        // Блокируем переход, т.к. внутри <a>
        e.preventDefault();
        e.stopPropagation();
        // При желании можно добавить логику подсветки активного размера
      });
    });
  });

  /****************************************************
   * 5. Детальная страница товара
   ****************************************************/
  // Переключение главного изображения при клике на миниатюры
  const mainImage = document.getElementById("mainImage");
  const thumbnails = document.querySelectorAll(".thumbnail");
  thumbnails.forEach((thumb) => {
    thumb.addEventListener("click", () => {
      if (!mainImage) return;
      const oldSrc = mainImage.src;
      mainImage.src = thumb.src;
      thumb.src = oldSrc;
    });
  });

  // Вкладки (Описание / Доп. информация)
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabPanels = document.querySelectorAll(".tab-panel");
  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabButtons.forEach((b) => b.classList.remove("active"));
      tabPanels.forEach((p) => p.classList.add("hidden"));

      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.remove("hidden");
      }
    });
  });

  // Подсветка выбранного цвета и размера (детальная страница)
  const detailColorSwatches = document.querySelectorAll(".color-swatch");
  detailColorSwatches.forEach((swatch) => {
    swatch.addEventListener("click", () => {
      detailColorSwatches.forEach((s) => s.classList.remove("active-color"));
      swatch.classList.add("active-color");
    });
  });

  const sizeButtons = document.querySelectorAll(".size-button");
  sizeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      sizeButtons.forEach((b) => b.classList.remove("active-size"));
      btn.classList.add("active-size");
    });
  });
});