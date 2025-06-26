# cart/session_cart.py

from decimal import Decimal
from typing import Iterator

from django.conf import settings
from store.models import Product

__all__ = ["Cart", "CART_SESSION_KEY"]

CART_SESSION_KEY = getattr(settings, "CART_SESSION_KEY", "cart")


class Cart:
    """Обёртка над request.session с удобными методами."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart: dict[str, dict] = cart
        self._changed: bool = False

    def add(self,
            product_id: int,
            qty: int = 1,
            *,
            size: str | None = None,
            color: int | None = None,
            update: bool = False) -> None:
        """Добавить товар или изменить количество."""
        # Ключ храним как "id" (цвет и размер хранятся внутри словаря)
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

    def __iter__(self) -> Iterator[dict]:
        """
        Итерируемся по товарам, обогащая их данными из БД:
        {
            "product": <Product>,
            "qty":     2,
            "size":    "M",
            "color":   5,
            "total":   Decimal('6980.00'),
        }
        """
        # Берём id товаров без учёта «:…»
        product_ids = [
            int(key.split(":", 1)[0])
            for key in self.cart.keys()
        ]
        products = Product.objects.in_bulk(product_ids)

        for key, item in list(self.cart.items()):
            pid = int(key.split(":", 1)[0])
            prod = products.get(pid)
            if prod is None:
                # товар удалили в БД — убираем из корзины
                del self.cart[key]
                self._changed = True
                continue

            yield {
                "product": prod,
                "qty":     item.get("qty", 0),
                "size":    item.get("size"),
                "color":   item.get("color"),
                "total":   prod.price * item.get("qty", 0),
            }

    def __len__(self) -> int:
        """Сколько позиций в корзине."""
        return len(self.cart)

    def total_qty(self) -> int:
        return sum(item.get("qty", 0) for item in self.cart.values())

    def total_price(self) -> Decimal:
        # Опять же, отрезаем всё после ":"
        product_ids = [
            int(key.split(":", 1)[0])
            for key in self.cart.keys()
        ]
        products = Product.objects.in_bulk(product_ids)
        total = Decimal("0")
        for key, item in self.cart.items():
            pid = int(key.split(":", 1)[0])
            prod = products.get(pid)
            if prod:
                total += prod.price * item.get("qty", 0)
        return total

    def _save(self) -> None:
        if self._changed:
            self.session[CART_SESSION_KEY] = self.cart
            self.session.modified = True
            self._changed = False

    def __del__(self):
        self._save()