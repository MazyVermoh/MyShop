from decimal import Decimal
from typing import Iterator, Optional, List

from django.conf import settings
from store.models import Product

__all__ = ["Cart", "CART_SESSION_KEY"]

CART_SESSION_KEY = getattr(settings, "CART_SESSION_KEY", "cart")


class Cart:
    """Обёртка над request.session с удобными методами, поддерживающая размер и цвет."""

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart: dict[str, dict] = cart
        self._changed: bool = False

    def _make_key(self, product_id: int, size: Optional[str], color: Optional[int]) -> str:
        """Собираем составной ключ: id:size:color"""
        parts: List[str] = [str(product_id)]
        if size:
            parts.append(size)
        if color is not None:
            parts.append(str(color))
        return ":".join(parts)

    def add(
        self,
        product_id: int,
        qty: int = 1,
        *,
        size: Optional[str] = None,
        color: Optional[int] = None,
        update: bool = False
    ) -> None:
        """Добавить товар или изменить количество (с учётом размера и цвета)."""
        key = self._make_key(product_id, size, color)
        if key not in self.cart:
            # Инициализируем новую запись
            self.cart[key] = {"qty": 0, "size": size, "color": color}
        if update:
            self.cart[key]["qty"] = qty
        else:
            self.cart[key]["qty"] += qty
        # Обновляем атрибуты на случай, если их изменили
        self.cart[key]["size"] = size
        self.cart[key]["color"] = color
        self._changed = True

    def remove(
        self,
        product_id: int,
        *,
        size: Optional[str] = None,
        color: Optional[int] = None
    ) -> None:
        """Удалить позицию: либо конкретную (с размером/цветом), либо все для данного товара."""
        if size is not None or color is not None:
            key = self._make_key(product_id, size, color)
            if key in self.cart:
                del self.cart[key]
                self._changed = True
        else:
            pid_str = str(product_id)
            # Удаляем все ключи с таким product_id
            keys_to_del = [k for k in self.cart if k.split(':', 1)[0] == pid_str]
            for k in keys_to_del:
                del self.cart[k]
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
        # Список всех product_id (до ":")
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
        # Суммируем отдельно, используя цены из БД
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
