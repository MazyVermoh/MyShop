document.addEventListener("DOMContentLoaded", function () {
  // Выпадающее меню в сайдбаре
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

  // Плавный слайдер с динамическим расчётом ширины слайда
  const productCards = document.querySelectorAll(".product-card");

  productCards.forEach((card) => {
    const carouselContainer = card.querySelector(".carousel-images");
    const images = card.querySelectorAll(".carousel-images img");
    const arrowLeft = card.querySelector(".arrow-left");
    const arrowRight = card.querySelector(".arrow-right");
    const dotsContainer = card.querySelector(".dots");

    if (!carouselContainer || !images.length) return;

    let currentIndex = 0;

    // Создание точек по количеству изображений
    dotsContainer.innerHTML = "";
    images.forEach((_, i) => {
      const dot = document.createElement("span");
      dot.classList.add("dot");
      dot.addEventListener("click", () => {
        currentIndex = i;
        updateCarousel();
      });
      dotsContainer.appendChild(dot);
    });

    function updateCarousel() {
      const slideWidth = carouselContainer.offsetWidth;
      carouselContainer.style.transform = `translateX(-${
        currentIndex * slideWidth
      }px)`;

      // Обновление состояния точек
      const allDots = dotsContainer.querySelectorAll(".dot");
      allDots.forEach((d) => d.classList.remove("active"));
      allDots[currentIndex]?.classList.add("active");

      // Скрытие стрелок, если изображение одно
      if (arrowLeft && arrowRight) {
        arrowLeft.style.display = images.length <= 1 ? "none" : "block";
        arrowRight.style.display = images.length <= 1 ? "none" : "block";
      }
    }

    // Инициализация слайдера
    updateCarousel();

    // Обработчики стрелок
    if (arrowLeft) {
      arrowLeft.addEventListener("click", () => {
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        updateCarousel();
      });
    }
    if (arrowRight) {
      arrowRight.addEventListener("click", () => {
        currentIndex = (currentIndex + 1) % images.length;
        updateCarousel();
      });
    }

    // Обновление слайдера при изменении размера окна
    window.addEventListener("resize", () => {
      updateCarousel();
    });

    // Логика для переключения цветов (в карточках каталога)
    const colorSwatches = card.querySelectorAll(".color-swatch");
    colorSwatches.forEach((swatch) => {
      swatch.addEventListener("click", () => {
        const color = swatch.getAttribute("data-color");
        const frontImage = card.getAttribute(`data-${color}-front`);
        const backImage = card.getAttribute(`data-${color}-back`);

        images[0].src = frontImage;
        images[1].src = backImage;

        currentIndex = 0;
        updateCarousel();
      });
    });
  });

  // --- Новый функционал: переключение вкладок на детальной странице товара ---
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabPanels = document.querySelectorAll(".tab-panel");

  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      // Убираем класс 'active' у всех кнопок
      tabButtons.forEach((b) => b.classList.remove("active"));
      // Скрываем все панели
      tabPanels.forEach((p) => p.classList.add("hidden"));

      // Делаем текущую кнопку активной
      btn.classList.add("active");
      // Отображаем нужную панель
      const targetId = btn.getAttribute("data-tab");
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.remove("hidden");
      }
    });
  });
});
