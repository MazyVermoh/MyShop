"""
Корзина на базе сессии.

В сессии храним так:
    {
        "<id>":             {"qty": 2},          # без размера
        "<id>:<SIZE>":      {"qty": 1},          # c размером
        ...
    }
Все значения JSON-совместимы, поэтому легко кладутся в request.session.
"""

from decimal import Decimal
from typing import Iterator

from django.conf import settings
from store.models import Product


__all__ = ["Cart", "CART_SESSION_KEY"]


CART_SESSION_KEY = getattr(settings, "CART_SESSION_KEY", "cart")


class Cart:
    """Обёртка над ``request.session`` с удобными методами."""

    # ─────────────────────────────────────────────────────────
    #  Инициализация
    # ─────────────────────────────────────────────────────────
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY) or {}
        self.cart: dict[str, dict] = cart           # ключи - строки
        self._changed: bool = False                 # чтобы не писать лишний раз

    # ─────────────────────────────────────────────────────────
    #  CRUD-методы
    # ─────────────────────────────────────────────────────────
    def _key(self, product_id: int, size: str | None = None) -> str:
        """Единая точка генерации ключа (id  или  id:SIZE)."""
        return f"{product_id}:{size.upper()}" if size else str(product_id)

    def add(
        self,
        product_id: int,
        qty: int = 1,
        *,
        size: str | None = None,
        update: bool = False,
    ) -> None:
        """
        Добавить товар в корзину.

        • если size передан ― позиция считается отдельной;
        • ``update=True`` — не увеличиваем, а ставим qty точно.
        """
        key = self._key(product_id, size)

        if key not in self.cart:
            self.cart[key] = {"qty": 0, "size": size}

        if update:
            self.cart[key]["qty"] = qty
        else:
            self.cart[key]["qty"] += qty

        self._changed = True

    def remove(self, product_id: int, *, size: str | None = None) -> None:
        """
        Удалить позицию (учитывает размер, если был указан).
        """
        key = self._key(product_id, size)
        if key in self.cart:
            del self.cart[key]
            self._changed = True

    def clear(self) -> None:
        self.session[CART_SESSION_KEY] = {}
        self.cart = self.session[CART_SESSION_KEY]
        self._changed = True

    # ─────────────────────────────────────────────────────────
    #  Итерация / подсчёты
    # ─────────────────────────────────────────────────────────
    def __iter__(self) -> Iterator[dict]:
        """
        Генерируем словари вида:

            {
                "product": <Product>,
                "qty":     2,
                "size":    "M" | None,
                "total":   Decimal('6980.00'),
            }
        """
        product_ids = [
            int(k.split(":", 1)[0]) for k in self.cart.keys()
        ]
        products = Product.objects.in_bulk(product_ids)

        for key, item in list(self.cart.items()):
            pid_str, *rest = key.split(":", 1)
            prod = products.get(int(pid_str))
            if prod is None:
                # товар удалён из БД → выбрасываем
                del self.cart[key]
                self._changed = True
                continue

            yield {
                "product": prod,
                "qty":     item["qty"],
                "size":    rest[0] if rest else None,
                "total":   prod.price * item["qty"],
            }

    def __len__(self) -> int:
        """Количество позиций (строк), а не штук."""
        return len(self.cart)

    def total_qty(self) -> int:
        """Сколько штук всего."""
        return sum(item["qty"] for item in self.cart.values())

    def total_price(self) -> Decimal:
        """Общая стоимость."""
        product_ids = [
            int(k.split(":", 1)[0]) for k in self.cart.keys()
        ]
        products = Product.objects.in_bulk(product_ids)

        total = Decimal(0)
        for key, item in self.cart.items():
            pid = int(key.split(":", 1)[0])
            prod = products.get(pid)
            if prod:
                total += prod.price * item["qty"]
        return total

    # ─────────────────────────────────────────────────────────
    #  Автосохранение перед завершением запроса
    # ─────────────────────────────────────────────────────────
    def _save(self) -> None:
        if self._changed:
            self.session[CART_SESSION_KEY] = self.cart
            self.session.modified = True
            self._changed = False

    def __del__(self):
        self._save()