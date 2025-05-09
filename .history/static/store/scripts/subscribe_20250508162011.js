// static/store/scripts/subscribe.js
document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("subscribe-form");
    const msg  = document.getElementById("subscribe-msg");
    if (!form) return;
  
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(form);
  
      try {
        const resp = await fetch(form.action, {
          method: "POST",
          body: formData,
          headers: {
            "X-Requested-With": "XMLHttpRequest",
          },
        });
        const data = await resp.json();
        msg.textContent = data.message || "Спасибо!";
        msg.style.color = data.ok ? "green" : "red";
      } catch {
        msg.textContent = "Ошибка сети, попробуйте позже";
        msg.style.color = "red";
      }
      form.reset();
    });
  });