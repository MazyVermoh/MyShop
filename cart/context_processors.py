# cart/context_processors.py
from cart.session_cart import Cart   # <-- ваш класс Cart


def cart_totals(request):
    """
    Добавляет в контекст две переменные:

    • cart_total_qty   — количество единиц товара (для бейджика «Корзина (N)»)
    • cart_total_price — сумма корзины Decimal ('3490.00')
    """
    cart = Cart(request)
    return {
        "cart_total_qty":   cart.total_qty(),
        "cart_total_price": cart.total_price(),
    }