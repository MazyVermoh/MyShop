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
   * 2. Карусель для карточек товаров
   ****************************************************/
  const productCards = document.querySelectorAll(".product-card");
  productCards.forEach((card) => {
    const carouselContainer = card.querySelector(".carousel-images");
    const images = card.querySelectorAll(".carousel-images img");
    const arrowLeft = card.querySelector(".arrow-left");
    const arrowRight = card.querySelector(".arrow-right");
    const dotsContainer = card.querySelector(".dots");

    // Если нет изображений, выходим
    if (!carouselContainer || images.length === 0) return;

    let currentIndex = 0;

    // Создаём "точки" (dots)
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

    function updateCarousel() {
      const slideWidth = carouselContainer.offsetWidth;
      carouselContainer.style.transform = `translateX(-${currentIndex * slideWidth}px)`;

      // Обновляем "активную" точку
      const allDots = dotsContainer.querySelectorAll(".dot");
      allDots.forEach((d) => d.classList.remove("active"));
      if (allDots[currentIndex]) {
        allDots[currentIndex].classList.add("active");
      }

      // Если 1 изображение – скрываем стрелки
      if (arrowLeft && arrowRight) {
        arrowLeft.style.display = images.length <= 1 ? "none" : "block";
        arrowRight.style.display = images.length <= 1 ? "none" : "block";
      }
    }

    // Инициализация
    updateCarousel();

    // Перехват клика стрелок, чтобы не переходить на детальную страницу
    if (arrowLeft) {
      arrowLeft.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        currentIndex = (currentIndex - 1 + images.length) % images.length;
        updateCarousel();
      });
    }

    if (arrowRight) {
      arrowRight.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        currentIndex = (currentIndex + 1) % images.length;
        updateCarousel();
      });
    }
    
    // Удалены обработчики для цветовых свотчей и размеров.
  });

  /****************************************************
   * 3. Детальная страница товара (если используется)
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

  // Вкладки
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

  // Удалены обработчики для детальной страницы, связанные с цветами и размерами.
});