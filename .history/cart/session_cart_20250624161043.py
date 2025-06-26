# cart/session_cart.py

"""
Корзина на базе сессии.

Теперь ключ в сессии — комбинация "product_id:size",
чтобы одна и та же футболка разных размеров шла разными строками.
"""

from decimal import Decimal
from typing import Iterator

from django.conf import settings
from store.models import Product


__all__ = ["Cart", "CART_SESSION_KEY"]


CART_SESSION_KEY = getattr(settings, "CART_SESSION_KEY", "cart")


class Cart:
    """Обёртка над ``request.session`` с удобными методами."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart: dict[str, dict] = cart
        self._changed = False

    def _key(self, product_id: int, size: str | None) -> str:
        """Уникальный ключ для product+size."""
        return f"{product_id}:{size or ''}"

    # ─── CRUD ────────────────────────────────────────────────────────
    def add(
        self,
        product_id: int,
        qty: int = 1,
        *,
        size: str | None = None,
        color: int | None = None,
        update: bool = False
    ) -> None:
        """
        Добавить или обновить количество для данной пары (product_id, size).
        """
        key = self._key(product_id, size)
        entry = self.cart.get(key, {"qty": 0, "size": size, "color": color})

        if update:
            entry["qty"] = qty
        else:
            entry["qty"] += qty

        # всегда сохраняем последние size/color
        entry["size"] = size
        entry["color"] = color

        self.cart[key] = entry
        self._changed = True

    def remove(self, product_id: int, *, size: str | None = None) -> None:
        """Удалить запись с данным product+size."""
        key = self._key(product_id, size)
        if key in self.cart:
            del self.cart[key]
            self._changed = True

    def clear(self) -> None:
        """Очистить всю корзину."""
        self.session[CART_SESSION_KEY] = {}
        self.cart = self.session[CART_SESSION_KEY]
        self._changed = True

    # ─── Итерация / подсчёты ───────────────────────────────────────────
    def __iter__(self) -> Iterator[dict]:
        """
        Итерируемся по записям, отдаём их в формате:
          {
            "product": <Product>,
            "qty":     int,
            "size":    str|None,
            "color":   int|None,
            "total":   Decimal,
          }
        """
        # собрать все product_id для одного запроса
        product_ids = {int(k.split(":", 1)[0]) for k in self.cart}
        products = Product.objects.in_bulk(product_ids)

        for key, data in self.cart.items():
            pid_str, _ = key.split(":", 1)
            pid = int(pid_str)
            prod = products.get(pid)
            if not prod:
                # если товар удалён из БД, убираем
                self.remove(pid, size=data.get("size"))
                continue

            yield {
                "product": prod,
                "qty":      data["qty"],
                "size":     data.get("size"),
                "color":    data.get("color"),
                "total":    prod.price * data["qty"],
            }

    def __len__(self) -> int:
        """Сколько строк в корзине (не суммарное кол-во)."""
        return len(self.cart)

    def total_qty(self) -> int:
        """Общее кол-во всех штук."""
        return sum(entry["qty"] for entry in self.cart.values())

    def total_price(self) -> Decimal:
        """Общая сумма всех строк."""
        product_ids = {int(k.split(":", 1)[0]) for k in self.cart}
        products = Product.objects.in_bulk(product_ids)
        total = Decimal("0")
        for key, data in self.cart.items():
            pid = int(key.split(":", 1)[0])
            prod = products.get(pid)
            if prod:
                total += prod.price * data["qty"]
        return total

    # ─── Сохранение в сессию ────────────────────────────────────────────
    def _save(self) -> None:
        if self._changed:
            self.session[CART_SESSION_KEY] = self.cart
            self.session.modified = True
            self._changed = False

    def __del__(self):
        self._save()