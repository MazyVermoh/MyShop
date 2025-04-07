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
   *     (работает, если в .product-card есть .carousel-images)
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

    // Создаём «точки» (dots)
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

      const allDots = dotsContainer.querySelectorAll(".dot");
      allDots.forEach((d) => d.classList.remove("active"));
      if (allDots[currentIndex]) {
        allDots[currentIndex].classList.add("active");
      }

      if (arrowLeft && arrowRight) {
        arrowLeft.style.display = images.length <= 1 ? "none" : "block";
        arrowRight.style.display = images.length <= 1 ? "none" : "block";
      }
    }

    updateCarousel();

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

    window.addEventListener("resize", () => {
      updateCarousel();
    });

    const colorSwatches = card.querySelectorAll(".color-swatch");
    colorSwatches.forEach((swatch) => {
      swatch.addEventListener("click", () => {
        const color = swatch.getAttribute("data-color");
        const frontImage = card.getAttribute(`data-${color}-front`);
        const backImage = card.getAttribute(`data-${color}-back`);
        if (images[0]) images[0].src = frontImage;
        if (images[1]) images[1].src = backImage;
        currentIndex = 0;
        updateCarousel();
      });
    });
  });

  /****************************************************
   *  3. Детальная страница товара (с множеством фото)
   ****************************************************/
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

  const detailColorSwatches = document.querySelectorAll(".color-swatch");
  detailColorSwatches.forEach((swatch) => {
    swatch.addEventListener("click", () => {
      detailColorSwatches.forEach((s) => s.classList.remove("active-color"));
      swatch.classList.add("active-color");
      const newFront = swatch.getAttribute("data-front");
      const newBack = swatch.getAttribute("data-back");
      if (mainImage && newFront) {
        mainImage.src = newFront;
      }
      if (thumbnails[0] && newBack) {
        thumbnails[0].src = newBack;
      }
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
