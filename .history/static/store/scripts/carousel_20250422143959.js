// static/store/scripts/carousel.js
document.addEventListener("DOMContentLoaded", function () {
  /****************************************************
   * 1. Выпадающее меню в сайдбаре (не менялось)
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

    // строим индикаторы
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

    function updateCarousel() {
      const slideWidth = carouselContainer.offsetWidth;
      carouselContainer.style.transform = `translateX(-${currentIndex * slideWidth}px)`;
      // активный индикатор
      dotsContainer.querySelectorAll(".dot").forEach((d, i) => {
        d.classList.toggle("active", i === currentIndex);
      });
      // видимость стрелок
      if (arrowLeft && arrowRight) {
        const show = images.length > 1;
        arrowLeft.style.display = show ? "block" : "none";
        arrowRight.style.display = show ? "block" : "none";
      }
    }

    // обработчики стрелок
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

    // ОБРАБОТЧИКИ СВОТЧЕЙ
    swatches.forEach((sw) => {
      sw.addEventListener("click", (e) => {
        e.stopPropagation();
        e.preventDefault();
        // вытаскиваем URL из data-атрибутов
        const front = sw.dataset.front;
        const back  = sw.dataset.back;
        const newImgs = [];
        if (front) newImgs.push(front);
        if (back)  newImgs.push(back);

        // если есть хотя бы одно изображение — подменяем карусель
        if (newImgs.length) {
          // очищаем контейнер
          carouselContainer.innerHTML = "";
          newImgs.forEach((src) => {
            const img = document.createElement("img");
            img.src = src;
            carouselContainer.appendChild(img);
          });
          // обновляем локальный массив и сбрасываем индекс
          images.length = 0;
          newImgs.forEach((src, i) => images.push(carouselContainer.children[i]));
          currentIndex = 0;
          buildDots();
          updateCarousel();
        }
      });
    });

    // инициализация
    buildDots();
    updateCarousel();
  });

  /****************************************************
   * 3. Детальная страница товара (не менялось)
   ****************************************************/
  const mainImage = document.getElementById("mainImage");
  const thumbnails = document.querySelectorAll(".thumbnail");
  thumbnails.forEach((thumb) => {
    thumb.addEventListener("click", () => {
      if (!mainImage) return;
      [mainImage.src, thumb.src] = [thumb.src, mainImage.src];
    });
  });

  const tabButtons = document.querySelectorAll(".tab-button");
  const tabPanels  = document.querySelectorAll(".tab-panel");
  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      tabButtons.forEach((b) => b.classList.remove("active"));
      tabPanels.forEach((p) => p.classList.add("hidden"));
      btn.classList.add("active");
      const target = btn.dataset.tab;
      document.getElementById(target)?.classList.remove("hidden");
    });
  });
});