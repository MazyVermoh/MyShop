// simple vanilla JS
document.addEventListener("DOMContentLoaded", () => {
    const table = document.getElementById("cartTable");
    if (!table) return;
  
    /** utils ---------------------------------------------------- */
    const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
    const fmt  = n => new Intl.NumberFormat("ru-RU").format(n) + " ₽";
  
    /** qty +/- -------------------------------------------------- */
    table.addEventListener("click", e => {
      const btn  = e.target.closest(".qty-btn");
      const rem  = e.target.closest(".remove-btn");
      const row  = e.target.closest("tr[data-id]");
      if (!row) return;
      const pid  = row.dataset.id;
  
      /* remove */
      if (rem) {
        fetch(`/cart/remove/${pid}/`, {
          method:"POST",
          headers:{ "X-CSRFToken": csrf, "X-Requested-With": "XMLHttpRequest" }
        }).then(r=>r.json()).then(data=>{
           row.remove();
           document.querySelector(".cart-link").innerHTML =
             `Корзина (${data.total_qty})`;
           document.getElementById("cartSum").textContent = fmt(data.total_price);
        });
        return;
      }
  
      /* qty change */
      if (btn) {
        const delta = parseInt(btn.dataset.delta,10);
        const qtyInp = row.querySelector(".qty-input");
        let newQty = Math.max(1, parseInt(qtyInp.value,10)+delta);
        fetch(`/cart/update/${pid}/`, {
          method:"POST",
          headers:{ "X-CSRFToken": csrf, "X-Requested-With": "XMLHttpRequest" },
          body:new URLSearchParams({ qty:newQty })
        }).then(r=>r.json()).then(data=>{
           qtyInp.value = newQty;
           row.querySelector(".row-total").textContent = fmt(data.row_total);
           document.querySelector(".cart-link").innerHTML =
             `Корзина (${data.total_qty})`;
           document.getElementById("cartSum").textContent = fmt(data.total_price);
        });
      }
    });
  });