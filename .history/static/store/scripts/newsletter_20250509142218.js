document.addEventListener("DOMContentLoaded", () => {
    const form = document.querySelector("#newsletter-form");
    if (!form) return;
  
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const email = form.email.value.trim();
      if (!email) return alert("Введите e‑mail");
  
      const csrftoken = document
        .querySelector("input[name=csrfmiddlewaretoken]")
        .value;
  
      try {
        const res = await fetch(form.action, {
          method: "POST",
          headers: {
            "X-CSRFToken": csrftoken,
            "X-Requested-With": "XMLHttpRequest",
          },
          body: new FormData(form),
        });
        if (res.ok) {
          form.reset();
          toast("Спасибо! Теперь вы в рассылке 🌟");
        } else {
          const data = await res.json();
          toast(data.errors.email[0].message || "Ошибка", true);
        }
      } catch {
        toast("Сбой сети — попробуйте позднее", true);
      }
    });
  
    // упрощённый toast
    function toast(msg, error = false) {
      const box = document.createElement("div");
      box.textContent = msg;
      box.className = "toast " + (error ? "toast--error" : "toast--ok");
      document.body.appendChild(box);
      setTimeout(() => box.remove(), 4000);
    }
  });