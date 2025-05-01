"""
Корзина на базе сессии.

В сессии хранится словарь вида:
    {
        "<product_id>": {
            "qty":  2,                 # количество
            "size": "M",               # выбранный размер (опц.)
            "color": 5,                # ID цвета     (опц.)
        },
        ...
    }

Все значения сериализуются в JSON-совместимые типы
(строки / числа) — так их легко класть в request.session.
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

        # при первом обращении кладём пустую корзину
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart: dict[str, dict] = cart
        self._changed: bool = False   # флаг, чтобы не писать в сессию лишний раз

    # ─────────────────────────────────────────────────────────────
    #  CRUD
    # ─────────────────────────────────────────────────────────────
    def add(self, product_id: int, qty: int = 1, *, size: str | None = None,
            color: int | None = None, update: bool = False) -> None:
        """Добавить товар или изменить количество."""
        pid = str(product_id)

        if pid not in self.cart:
            self.cart[pid] = {"qty": 0}

        if size is not None:
            self.cart[pid]["size"] = size
        if color is not None:
            self.cart[pid]["color"] = color

        if update:
            self.cart[pid]["qty"] = qty
        else:
            self.cart[pid]["qty"] += qty

        self._changed = True

    def remove(self, product_id: int) -> None:
        pid = str(product_id)
        if pid in self.cart:
            del self.cart[pid]
            self._changed = True

    def clear(self) -> None:
        self.session[CART_SESSION_KEY] = {}
        self.cart = self.session[CART_SESSION_KEY]
        self._changed = True

    # ─────────────────────────────────────────────────────────────
    #  Итерация / подсчёты
    # ─────────────────────────────────────────────────────────────
    def __iter__(self) -> Iterator[dict]:
        """
        Итерируемся по товарам, обогащая их данными из БД:

        {
            "product":  <Product>,
            "qty":      2,
            "size":     "M",
            "color":    5,
            "total":    Decimal('6980.00'),
        }
        """
        product_ids = [int(pid) for pid in self.cart.keys()]
        products = Product.objects.in_bulk(product_ids)

        for pid, item in self.cart.items():
            prod = products.get(int(pid))
            if prod is None:
                # товар удалили из БД — убираем из корзины
                self.remove(pid)
                continue

            enriched = {
                "product": prod,
                "qty":     item["qty"],
                "size":    item.get("size"),
                "color":   item.get("color"),
                "total":   prod.price * item["qty"],
            }
            yield enriched

    def __len__(self) -> int:
        """Сколько позиций в корзине (не товаров)."""
        return len(self.cart)

    def total_qty(self) -> int:
        return sum(item["qty"] for item in self.cart.values())

    def total_price(self) -> Decimal:
        product_ids = [int(pid) for pid in self.cart.keys()]
        products = Product.objects.in_bulk(product_ids)
        total = Decimal(0)

        for pid, item in self.cart.items():
            prod = products.get(int(pid))
            if prod:
                total += prod.price * item["qty"]
        return total

    # ─────────────────────────────────────────────────────────────
    #  Сохранение в сессию (вызывается автоматически)
    # ─────────────────────────────────────────────────────────────
    def _save(self) -> None:
        if self._changed:
            self.session[CART_SESSION_KEY] = self.cart
            self.session.modified = True
            self._changed = False

    # make sure save happens when request-response цикл заканчивается
    def __del__(self):
        self._save()