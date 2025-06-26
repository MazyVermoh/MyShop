# cart/session_cart.py

from decimal import Decimal
from typing import Iterator, Optional

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
        self._changed = False

    def add(self,
            product_id: int,
            qty: int = 1,
            *,
            size: Optional[str] = None,
            color: Optional[int] = None,
            update: bool = False) -> None:
        """
        Добавить товар или изменить количество.
        Ключ в сессии = "<product_id>:<size>" если размер задан, иначе просто "<product_id>".
        """
        key = f"{product_id}:{size}" if size else str(product_id)

        if key not in self.cart:
            self.cart[key] = {"qty": 0}

        # Сохраняем размер/цвет в случае AJAX-запросов
        if size is not None:
            self.cart[key]["size"] = size
        if color is not None:
            self.cart[key]["color"] = color

        if update:
            self.cart[key]["qty"] = qty
        else:
            self.cart[key]["qty"] += qty

        self._changed = True

    def remove(self, product_id: int, size: Optional[str] = None) -> None:
        """
        Удалить позицию. Учитывает размер в ключе.
        """
        key = f"{product_id}:{size}" if size else str(product_id)
        if key in self.cart:
            del self.cart[key]
            self._changed = True

    def clear(self) -> None:
        self.session[CART_SESSION_KEY] = {}
        self.cart = self.session[CART_SESSION_KEY]
        self._changed = True

    def __iter__(self) -> Iterator[dict]:
        """
        Итерируемся по позициям корзины, отдавая:
        {
          "product": <Product>,
          "qty": int,
          "size": Optional[str],
          "color": Optional[int],
          "total": Decimal,
        }
        """
        # Сначала соберём все product_id
        mapping: dict[str, tuple[int, Optional[str]]] = {}
        product_ids: list[int] = []

        for raw_key in self.cart:
            if ":" in raw_key:
                pid_str, sz = raw_key.split(":", 1)
            else:
                pid_str, sz = raw_key, self.cart[raw_key].get("size")
            try:
                pid = int(pid_str)
            except ValueError:
                continue
            product_ids.append(pid)
            mapping[raw_key] = (pid, sz)

        products = Product.objects.in_bulk(product_ids)

        for raw_key, data in self.cart.items():
            pid, sz = mapping.get(raw_key, (None, None))
            prod = products.get(pid)
            if not prod:
                # Если товара уже нет в БД — удаляем
                self.remove(pid, sz)
                continue

            yield {
                "product": prod,
                "qty":     data.get("qty", 0),
                "size":    sz,
                "color":   data.get("color"),
                "total":   prod.price * data.get("qty", 0),
            }

    def __len__(self) -> int:
        # Количество слотов (разных размеров) в корзине
        return len(self.cart)

    def total_qty(self) -> int:
        # Суммарное кол-во товаров
        return sum(data.get("qty", 0) for data in self.cart.values())

    def total_price(self) -> Decimal:
        # Общая сумма по всем позициям
        mapping = []
        for raw_key in self.cart:
            pid_str = raw_key.split(":", 1)[0]
            try:
                mapping.append(int(pid_str))
            except ValueError:
                continue

        products = Product.objects.in_bulk(mapping)
        total = Decimal("0")
        for raw_key, data in self.cart.items():
            pid = int(raw_key.split(":", 1)[0])
            prod = products.get(pid)
            if prod:
                total += prod.price * data.get("qty", 0)
        return total

    def _save(self) -> None:
        if self._changed:
            self.session[CART_SESSION_KEY] = self.cart
            self.session.modified = True
            self._changed = False

    def __del__(self):
        # Авто-сохранение в сессию
        self._save()