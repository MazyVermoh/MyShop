document.addEventListener("DOMContentLoaded", () => {
  // Контейнер с элементами корзины
  const container = document.getElementById("cartTable");
  if (!container) return;

  /* ---- CSRF-токен из cookie --------------------------------- */
  const getCookie = (name) => {
    const m = document.cookie.match(
      new RegExp("(?:^|; )" + name.replace(/[$()*+./?[\\\]^{|}-]/g, "\\$&") + "=([^;]*)")
    );
    return m ? decodeURIComponent(m[1]) : "";
  };
  const CSRF = getCookie("csrftoken");
  const HDRS = {
    "X-CSRFToken": CSRF,
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/x-www-form-urlencoded",
  };

  /* ---- форматирование цены ------------------------------ */
  const fmt = (n) => new Intl.NumberFormat("ru-RU").format(n) + " ₽";

  /* ---- утилита для body-payload ------------------------------ */
  const encBody = (obj) =>
    Object.entries(obj)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
      .join("&");

  /* ---- делегирование кликов внутри контейнера -------------------------- */
  container.addEventListener("click", (e) => {
    const itemElem = e.target.closest(".cart-item[data-id]");
    if (!itemElem) return;

    const pid = itemElem.dataset.id;
    const size = itemElem.dataset.size || "";
    const color = itemElem.dataset.color || "";

    const minusBtn = e.target.closest(".qty-btn[data-delta='-1']");
    const plusBtn  = e.target.closest(".qty-btn[data-delta='1']");
    const delBtn   = e.target.closest(".remove-btn");

    /* --- удалить позицию -------------------------------------- */
    if (delBtn) {
      fetch(`/cart/remove/${pid}/`, {
        method: "POST",
        headers: HDRS,
        body: encBody({ size, color }),
      })
        .then((r) => r.json())
        .then((data) => updateUI({ remove: true, itemElem, data }));
      return;
    }

    /* --- изменить количество ---------------------------------- */
    if (minusBtn || plusBtn) {
      const qtyInput = itemElem.querySelector(".qty-input");
      let newQty = parseInt(qtyInput.value, 10) + (plusBtn ? 1 : -1);
      if (newQty < 1) newQty = 1;

      fetch(`/cart/update/${pid}/`, {
        method: "POST",
        headers: HDRS,
        body: encBody({ qty: newQty, size, color }),
      })
        .then((r) => r.json())
        .then((data) => updateUI({ newQty, itemElem, data }));
    }
  });

  /* ---- обновляем DOM / счётчики ------------------------------ */
  function updateUI({ remove = false, newQty = null, itemElem, data }) {
    if (remove) {
      itemElem.remove();
    } else {
      itemElem.querySelector(".qty-input").value = newQty;
      itemElem.querySelector(".row-total").textContent = fmt(data.row_total);
      const minus = itemElem.querySelector(".qty-btn[data-delta='-1']");
      if (minus) minus.disabled = newQty <= 1;
    }

    const cartLink = document.querySelector(".cart-link");
    if (cartLink) cartLink.textContent = `Корзина (${data.total_qty})`;

    const cartSum = document.getElementById("cartSum");
    if (cartSum) cartSum.textContent = fmt(data.total_price);

    if (data.total_qty === 0) location.reload();
  }
});