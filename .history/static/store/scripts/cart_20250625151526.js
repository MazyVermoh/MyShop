/* static/store/scripts/cart.js
   ──────────────────────────────────────────────────────────────
   •  Ajax-обновление количества (±) и удаление позиции.
   •  Работает даже если одна и та же модель лежит в корзине в разных
      размерах: строка <tr> отдаёт и data-id, и data-size.
   ────────────────────────────────────────────────────────────── */

document.addEventListener("DOMContentLoaded", () => {
  const table = document.getElementById("cartTable");
  if (!table) return;

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
  const fmt = (n) => new Intl.NumberFormat("ru-RU").format(n) + " ₽";

  /* ---- утилита для body-payload ------------------------------ */
  const encBody = (obj) =>
    Object.entries(obj)
      .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
      .join("&");

  /* ---- обработчик кликов по таблице -------------------------- */
  table.addEventListener("click", (e) => {
    const row = e.target.closest("tr[data-id]");
    if (!row) return;

    const pid = row.dataset.id;
    const size = row.dataset.size || "";
    const minus = e.target.closest(".qty-btn[data-delta='-1']");
    const plus = e.target.closest(".qty-btn[data-delta='1']");
    const del = e.target.closest(".remove-btn");

    /* --- удалить позицию -------------------------------------- */
    if (del) {
      fetch(`/cart/remove/${pid}/`, {
        method: "POST",
        headers: HDRS,
        body: encBody({ size }),
      })
        .then((r) => r.json())
        .then((data) => updateUI({ remove: true, row, data }));
      return;
    }

    /* --- изменить количество ---------------------------------- */
    if (minus || plus) {
      const qtyInp = row.querySelector(".qty-input");
      let newQty = parseInt(qtyInp.value, 10) + (plus ? 1 : -1);
      if (newQty < 1) newQty = 1;

      fetch(`/cart/update/${pid}/`, {
        method: "POST",
        headers: HDRS,
        body: encBody({ qty: newQty, size }),
      })
        .then((r) => r.json())
        .then((data) => updateUI({ newQty, row, data }));
    }
  });

  /* ---- обновляем DOM / счётчики ------------------------------ */
  function updateUI({ remove = false, newQty = null, row, data }) {
    if (remove) {
      row.remove();
    } else {
      row.querySelector(".qty-input").value = newQty;
      row.querySelector(".row-total").textContent = fmt(data.row_total);
      /* блокируем «−», если 1 шт. */
      const minusBtn = row.querySelector(".qty-btn[data-delta='-1']");
      minusBtn.disabled = newQty <= 1;
    }

    /* глобальный счётчик / сумма */
    document.querySelector(".cart-link").textContent = `Корзина (${data.total_qty})`;
    document.getElementById("cartSum").textContent = fmt(data.total_price);

    /* если корзина опустела — мягко перезагружаем страницу,
       чтобы показать сообщение «Корзина пуста» */
    if (data.total_qty === 0) location.reload();
  }
});