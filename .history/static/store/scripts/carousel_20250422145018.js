// static/store/scripts/carousel.js

document.addEventListener("DOMContentLoaded", function () {
  /****************************************************
   * 1. Выпадающее меню в сайдбаре
   ****************************************************/
  const dropdowns = document.querySelectorAll(".dropdown");
  dropdowns.forEach((dropdown) => {
    const sidebarArrow = dropdown.querySelector(".sidebar-arrow");
    const dropdownAnchor = dropdown.querySelector("a");

    function toggleDropdown(e) {
      e.preventDefault();
      dropdown.classList.toggle("active");
    }

    if (sidebarArrow) {
      sidebarArrow.addEventListener("click", toggleDropdown);
    }
    if (dropdownAnchor) {
      dropdownAnchor.addEventListener("click", toggleDropdown);
    }
  });

  /****************************************************
   * 2. Карусель для карточек товаров + свотчи
   ****************************************************/
  const productCards = document.querySelectorAll(".product-card");
  productCards.forEach((card) => {
    const carouselContainer = card.querySelector(".carousel-images");
    const images = Array.from(card.querySelectorAll(".carousel-images img"));
    const arrowLeft = card.querySelector(".arrow-left");
    const arrowRight = card.querySelector(".arrow-right");
    const dotsContainer = card.querySelector(".dots");
    const swatches = card.querySelectorAll(".color-swatch");

    if (!carouselContainer || images.length === 0) return;

    let currentIndex = 0;

    // Построить точки-индикаторы
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

    // Обновить позицию карусели и активность элементов
    function updateCarousel() {
      const slideWidth = carouselContainer.offsetWidth;
      carouselContainer.style.transform = `translateX(-${currentIndex * slideWidth}px)`;

      // Активная точка
      dotsContainer.querySelectorAll(".dot").forEach((d, i) => {
        d.classList.toggle("active", i === currentIndex);
      });

      // Показать/скрыть стрелки
      if (arrowLeft && arrowRight) {
        const show = images.length > 1;
        arrowLeft.style.display = show ? "block" : "none";
        arrowRight.style.display = show ? "block" : "none";
      }
    }

    // Обработчики стрелок
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

    // Обработчики цветных свотчей
    swatches.forEach((sw) => {
      sw.addEventListener("click", (e) => {
        e.stopPropagation();
        e.preventDefault();

        // считываем URL фронт‑ и бэк‑изображений из data-атрибутов
        const front = sw.dataset.front;
        const back  = sw.dataset.back;
        const newUrls = [];
        if (front) newUrls.push(front);
        if (back)  newUrls.push(back);

        if (newUrls.length) {
          // заменить содержимое карусели
          carouselContainer.innerHTML = "";
          newUrls.forEach((src) => {
            const img = document.createElement("img");
            img.src = src;
            img.alt = "";
            carouselContainer.appendChild(img);
          });

          // обновить локальный массив изображений
          images.length = 0;
          carouselContainer.querySelectorAll("img").forEach((img) => {
            images.push(img);
          });

          currentIndex = 0;
          buildDots();
          updateCarousel();
        }
      });
    });

    // Инициализация карусели
    buildDots();
    updateCarousel();
  });

  /****************************************************
   * 3. Детальная страница товара: переключение миниатюр
   ****************************************************/
  const mainImage = document.getElementById("mainImage");
  const thumbnails = document.querySelectorAll(".thumbnail");
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
      // переключить кнопку
      tabButtons.forEach((b) => b.classList.toggle("active", b === btn));
      // показать нужную панель
      const targetId = btn.dataset.tab;
      tabPanels.forEach((panel) => {
        panel.classList.toggle("hidden", panel.id !== targetId);
      });
    });
  });
});