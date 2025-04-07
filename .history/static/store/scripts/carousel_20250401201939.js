document.addEventListener("DOMContentLoaded", function () {
  /****************************************************
   *  1. Выпадающее меню в сайдбаре
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
   *  2. Плавный слайдер/карусель для карточек в каталоге
   *     (только если в .product-card есть .carousel-images)
   ****************************************************/
  const productCards = document.querySelectorAll(".product-card");
  productCards.forEach((card) => {
    const carouselContainer = card.querySelector(".carousel-images");
    const images = card.querySelectorAll(".carousel-images img");
    const arrowLeft = card.querySelector(".arrow-left");
    const arrowRight = card.querySelector(".arrow-right");
    const dotsContainer = card.querySelector(".dots");

    if (!carouselContainer || images.length === 0) return;

    let currentIndex = 0;

    // Создаём «точки» (dots) по количеству изображений
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

      // Обновляем «активную точку»
      const allDots = dotsContainer.querySelectorAll(".dot");
      allDots.forEach((d) => d.classList.remove("active"));
      if (allDots[currentIndex]) {
        allDots[currentIndex].classList.add("active");
      }

      // Скрыть стрелки, если только 1 изображение
      if (arrowLeft && arrowRight) {
        arrowLeft.style.display = images.length <= 1 ? "none" : "block";
        arrowRight.style.display = images.length <= 1 ? "none" : "block";
      }
    }

    // Инициализация
    updateCarousel();

    // Стрелки «влево», «вправо»
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

    // Пересчитываем ширину при ресайзе окна
    window.addEventListener("resize", () => {
      updateCarousel();
    });

    // Если в карточке есть цветовые свотчи — для каталога
    const colorSwatches = card.querySelectorAll(".color-swatch");
    colorSwatches.forEach((swatch) => {
      swatch.addEventListener("click", () => {
        const color = swatch.getAttribute("data-color");
        const frontImage = card.getAttribute(`data-${color}-front`);
        const backImage = card.getAttribute(`data-${color}-back`);

        // Меняем первые 2 изображения в блоке carousel-images
        if (images[0]) images[0].src = frontImage;
        if (images[1]) images[1].src = backImage;

        currentIndex = 0;
        updateCarousel();
      });
    });
  });

  /****************************************************
   *  3. Детальная страница товара
   ****************************************************/

  // 3.1. «Swap» при клике на миниатюру
  const mainImage = document.getElementById("mainImage");
  const thumbnail = document.querySelector(".thumbnail");
  if (mainImage && thumbnail) {
    thumbnail.addEventListener("click", () => {
      // Меняем src местами
      const oldSrc = mainImage.src;
      mainImage.src = thumbnail.src;
      thumbnail.src = oldSrc;
    });
  }

  // 3.2. Переключение вкладок (Описание / Additional Info)
  const tabButtons = document.querySelectorAll(".tab-button");
  const tabPanels = document.querySelectorAll(".tab-panel");
  tabButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      // Снимаем класс active у всех кнопок
      tabButtons.forEach((b) => b.classList.remove("active"));
      // Скрываем все панели
      tabPanels.forEach((p) => p.classList.add("hidden"));

      // Текущая кнопка становится активной
      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetPanel = document.getElementById(targetId);
      if (targetPanel) {
        targetPanel.classList.remove("hidden");
      }
    });
  });

  // 3.3. Подсветка цвета + смена картинки при клике на color-swatch
  const detailColorSwatches = document.querySelectorAll(".color-swatch");
  detailColorSwatches.forEach((swatch) => {
    swatch.addEventListener("click", () => {
      // Удаляем «active-color» у всех
      detailColorSwatches.forEach((s) => s.classList.remove("active-color"));
      // Подсвечиваем текущий
      swatch.classList.add("active-color");

      // Считываем data-front и data-back
      const newFront = swatch.getAttribute("data-front");
      const newBack = swatch.getAttribute("data-back");

      // Если хотим сразу заменить mainImage на newFront
      if (mainImage && newFront) {
        mainImage.src = newFront;
      }

      // Если хотим также поменять миниатюру на newBack
      if (thumbnail && newBack) {
        thumbnail.src = newBack;
      }
    });
  });

  // 3.4. Подсветка выбранного размера
  const sizeButtons = document.querySelectorAll(".size-button");
  sizeButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      sizeButtons.forEach((b) => b.classList.remove("active-size"));
      btn.classList.add("active-size");
      // Здесь можно сохранить инфу о выбранном размере для корзины...
    });
  });
});
