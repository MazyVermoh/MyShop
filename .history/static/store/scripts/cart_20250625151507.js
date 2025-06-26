// static/store/scripts/cart.js  (перезаписать полностью)
document.addEventListener("DOMContentLoaded", () => {
    const table = document.getElementById("cartTable");
    if (!table) return;
  
    /* --- CSRF из cookie --------------------------------------- */
    const getCookie = name => {
      const m = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
      return m ? decodeURIComponent(m[1]) : "";
    };
    const csrf = getCookie("csrftoken");
    const hdrs = {
      "X-CSRFToken": csrf,
      "X-Requested-With": "XMLHttpRequest",
      "Content-Type": "application/x-www-form-urlencoded"
    };
    const fmt = n => new Intl.NumberFormat("ru-RU").format(n) + " ₽";
  
    /* --- обработчик кликов ----------------------------------- */
    table.addEventListener("click", e => {
      const row = e.target.closest("tr[data-id]");
      if (!row) return;
      const pid   = row.dataset.id;
      const minus = e.target.closest(".qty-btn[data-delta='-1']");
      const plus  = e.target.closest(".qty-btn[data-delta='1']");
      const del   = e.target.closest(".remove-btn");
  
      /* удалить товар */
      if (del) {
        fetch(`/cart/remove/${pid}/`, {method:"POST", headers:hdrs})
          .then(r=>r.json()).then(updateUI.bind(null,row,false));
        return;
      }
  
      /* изменить количество */
      if (minus || plus) {
        const qtyInp = row.querySelector(".qty-input");
        let newQty = parseInt(qtyInp.value,10) + (plus ? 1 : -1);
        if (newQty < 1) newQty = 1;           // минимально 1
  
        fetch(`/cart/update/${pid}/`, {
          method:"POST",
          headers:hdrs,
          body:`qty=${newQty}`
        }).then(r=>r.json()).then(data=>{
          if (newQty === 0) {
            updateUI(row,false,data);
          } else {
            updateUI(row,newQty,data);
          }
        });
      }
    });
  
    /* --- общая функция обновления DOM ------------------------- */
    function updateUI(row,newQty,data){
      if (newQty) {
        row.querySelector(".qty-input").value = newQty;
        row.querySelector(".row-total").textContent = fmt(data.row_total);
      } else {
        row.remove();
      }
      document.querySelector(".cart-link").innerHTML =
        `Корзина (${data.total_qty})`;
      document.getElementById("cartSum").textContent = fmt(data.total_price);
    }
  });