from decimal import Decimal
from django.conf import settings
from store.models import Product   # импортируем ваши товары


class SessionCart:
    """
    Корзина, хранящаяся **в сессии**.
    Ключ сессии задаётся в settings.CART_SESSION_ID (по умолчанию "cart").
    Элементы храним так:
        {
            "12": {            # product.id в строке
                "price": "3490.00",   # строкой, чтобы сериализовалось
                "qty": 2,
                "name": "Lionel Messi Tee",
            },
            ...
        }
    """

    def __init__(self, request):
        self.session = request.session
        self.key = getattr(settings, "CART_SESSION_ID", "cart")
        cart = self.session.get(self.key)
        if cart is None:
            cart = self.session[self.key] = {}
        self.cart = cart

    # ───────────────────────── базовые операции ──────────────────────────
    def __len__(self):
        """Кол-во всех единиц товара (для значка Cart(Х))."""
        return sum(item["qty"] for item in self.cart.values())

    def __iter__(self):
        """
        Итерируемся по **товарам** в корзине.
        Каждому словарю добавляем объект `product` и `total_price`.
        """
        product_ids = self.cart.keys()
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for p in products:
            item = cart[str(p.id)]
            item["product"] = p
            item["total_price"] = Decimal(item["price"]) * item["qty"]
            yield item

    # ───────────────────────── публичный API ─────────────────────────────
    def add(self, product: Product, qty: int = 1, update: bool = False):
        """Добавить товар.  `update=True` → заменить количество."""
        pid = str(product.id)
        if pid not in self.cart:
            self.cart[pid] = {
                "price": str(product.price),
                "qty": 0,
                "name": product.name,
            }
        if update:
            self.cart[pid]["qty"] = qty
        else:
            self.cart[pid]["qty"] += qty
        self._save()

    def remove(self, product: Product):
        pid = str(product.id)
        if pid in self.cart:
            del self.cart[pid]
            self._save()

    def clear(self):
        self.session[self.key] = {}
        self.session.modified = True

    # ───────────────────────── helpers ───────────────────────────────────
    def get_subtotal(self) -> Decimal:
        return sum(Decimal(item["price"]) * item["qty"] for item in self.cart.values())

    def _save(self):
        """Помечаем сессию изменённой, чтобы Django сохранил её в БД."""
        self.session[self.key] = self.cart
        self.session.modified = True